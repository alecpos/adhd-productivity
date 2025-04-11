"""Task analyzer service module."""

from typing import Dict, Any, List, Optional, Union
from uuid import UUID
import logging
import json
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.services.base_service import BaseService, OPEN, CLOSED, HALF_OPEN
from app.models.task_model import TaskModel

class TaskAnalyzerService(BaseService):
    """Service for analyzing tasks and providing insights."""

    def __init__(self, db: AsyncSession, llm_service=None):
        """Initialize the service with database session and optional LLM service."""
        super().__init__(db, TaskModel, None)  # Pass TaskModel and None for schema
        self.logger = logging.getLogger(self.__class__.__name__)
        self.llm_service = llm_service

    @BaseService.with_retry(
        max_retries=3,
        initial_delay=0.1,
        max_delay=2.0,
        backoff_factor=2.0,
        error_message="Failed to analyze task"
    )
    @BaseService.with_circuit_breaker(
        name="task_analysis",
        failure_threshold=5,
        recovery_timeout=30
    )
    async def analyze_task(self, task_id: UUID) -> Dict[str, Any]:
        """Analyze a task and return insights.

        This method:
        1. Fetches the task details
        2. Analyzes the content using NLP techniques
        3. Estimates cognitive load and difficulty
        4. Identifies related tasks and potential dependencies
        5. Returns a comprehensive analysis
        """
        self.logger.info(f"Starting analysis for task {task_id}")

        # Fetch task
        query = select(TaskModel).where(TaskModel.id == task_id)
        result = await self.db.execute(query)
        task = result.scalar_one_or_none()

        if not task:
            self.logger.warning(f"Task {task_id} not found")
            return {"error": "Task not found"}

        try:
            # Basic analysis
            word_count = len(task.title.split()) + len(task.description.split() if task.description else [])
            estimated_minutes = max(15, word_count * 2)  # Simple estimation

            # Advanced analysis using bulkhead pattern
            advanced_analysis = await self._analyze_task_content(task)

            analysis = {
                "task_id": str(task.id),
                "user_id": str(task.user_id),
                "title": task.title,
                "timestamp": datetime.utcnow().isoformat(),
                "basic_metrics": {
                    "word_count": word_count,
                    "estimated_minutes": estimated_minutes,
                },
                "cognitive_analysis": {
                    "cognitive_load": advanced_analysis.get("cognitive_load", 5),
                    "focus_required": advanced_analysis.get("focus_required", "medium"),
                    "energy_level": advanced_analysis.get("energy_level", "medium"),
                    "best_time_of_day": advanced_analysis.get("best_time_of_day", "morning"),
                },
                "category": advanced_analysis.get("category", "uncategorized"),
                "tags": advanced_analysis.get("tags", []),
                "related_tasks": advanced_analysis.get("related_tasks", []),
            }

            # Save analysis to task (in a real implementation)
            # task.analysis_data = json.dumps(analysis)
            # await self.db.commit()

            self.logger.info(f"Analysis completed for task {task_id}")
            return analysis

        except Exception as e:
            self.logger.error(f"Error analyzing task {task_id}: {str(e)}", exc_info=True)
            raise

    async def _analyze_task_content(self, task: TaskModel) -> Dict[str, Any]:
        """Analyze task content using NLP or LLM, with bulkhead pattern."""
        try:
            # Use bulkhead pattern to isolate potentially resource-intensive LLM calls
            if self.llm_service:
                try:
                    # Call LLM service with timeout
                    result = await self.bulkhead(
                        self._call_llm_analysis,
                        task.title,
                        task.description,
                        timeout=5
                    )
                    return result
                except Exception as e:
                    self.logger.warning(f"LLM analysis failed: {str(e)}, falling back to basic analysis")

            # Fallback to basic analysis
            return self._basic_task_analysis(task)

        except Exception as e:
            self.logger.error(f"Error in _analyze_task_content: {str(e)}", exc_info=True)
            # Return safe defaults
            return {
                "cognitive_load": 5,
                "focus_required": "medium",
                "energy_level": "medium",
                "best_time_of_day": "morning",
                "category": "uncategorized",
                "tags": []
            }

    async def _call_llm_analysis(self, title: str, description: str) -> Dict[str, Any]:
        """Call LLM service to analyze task content."""
        # In a real implementation, this would call the LLM service
        # For now, return a mock response
        if not self.llm_service:
            raise ValueError("LLM service not available")

        # This would be an actual call to the LLM service
        analysis = await self.llm_service.analyze_text(
            prompt=f"Task: {title}\nDescription: {description}\n\nAnalyze this task and provide cognitive load (1-10), focus required (low/medium/high), energy level (low/medium/high), best time of day, category, and relevant tags."
        )

        return analysis

    def _basic_task_analysis(self, task: TaskModel) -> Dict[str, Any]:
        """Perform basic task analysis without LLM."""
        # Simple rule-based analysis
        title_lower = task.title.lower()
        desc_lower = task.description.lower() if task.description else ""
        combined = f"{title_lower} {desc_lower}"

        # Simple keyword matching
        cognitive_load = 5  # Default medium
        focus_required = "medium"  # Default medium
        energy_level = "medium"  # Default medium
        best_time_of_day = "morning"  # Default morning

        # Adjust cognitive load based on keywords
        high_load_keywords = ["complex", "difficult", "challenging", "analyze", "design"]
        low_load_keywords = ["simple", "easy", "quick", "brief", "routine"]

        for keyword in high_load_keywords:
            if keyword in combined:
                cognitive_load += 1

        for keyword in low_load_keywords:
            if keyword in combined:
                cognitive_load -= 1

        # Clamp to 1-10 range
        cognitive_load = max(1, min(10, cognitive_load))

        # Determine focus level
        if cognitive_load >= 7:
            focus_required = "high"
        elif cognitive_load <= 3:
            focus_required = "low"

        # Determine energy level based on length and cognitive load
        word_count = len(combined.split())
        if word_count > 100 or cognitive_load >= 7:
            energy_level = "high"
        elif word_count < 30 and cognitive_load <= 3:
            energy_level = "low"

        # Determine best time based on cognitive load and energy
        if cognitive_load >= 7 or energy_level == "high":
            best_time_of_day = "morning"
        elif 4 <= cognitive_load <= 6:
            best_time_of_day = "afternoon"
        else:
            best_time_of_day = "evening"

        # Determine category based on keywords
        categories = {
            "work": ["project", "meeting", "deadline", "client", "report"],
            "personal": ["family", "friend", "hobby", "health", "exercise"],
            "learning": ["study", "read", "course", "learn", "education"],
            "errands": ["buy", "shop", "clean", "call", "appointment"],
            "creative": ["design", "write", "create", "brainstorm", "draw"]
        }

        category = "uncategorized"
        max_matches = 0

        for cat, keywords in categories.items():
            matches = sum(1 for keyword in keywords if keyword in combined)
            if matches > max_matches:
                max_matches = matches
                category = cat

        # Generate tags
        all_keywords = []
        for cat_keywords in categories.values():
            all_keywords.extend(cat_keywords)

        tags = [keyword for keyword in all_keywords if keyword in combined]

        return {
            "cognitive_load": cognitive_load,
            "focus_required": focus_required,
            "energy_level": energy_level,
            "best_time_of_day": best_time_of_day,
            "category": category,
            "tags": tags[:5]  # Limit to 5 tags
        }

    @BaseService.with_retry(
        max_retries=2,
        initial_delay=0.1,
        error_message="Failed to generate task insights"
    )
    async def generate_task_insights(self, user_id: UUID) -> Dict[str, Any]:
        """Generate insights across all user tasks."""
        self.logger.info(f"Generating task insights for user {user_id}")

        try:
            # Get all user tasks
            query = select(TaskModel).where(TaskModel.user_id == user_id)
            result = await self.db.execute(query)
            tasks = result.scalars().all()

            if not tasks:
                return {"error": "No tasks found", "insights": []}

            # Calculate basic metrics
            total_tasks = len(tasks)
            completed_tasks = sum(1 for task in tasks if task.status == "COMPLETED")
            overdue_tasks = sum(1 for task in tasks if task.due_date and task.due_date < datetime.utcnow() and task.status != "COMPLETED")

            # Calculate completion rate
            completion_rate = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0

            # Calculate average cognitive load (if available)
            cognitive_loads = [getattr(task, "cognitive_load", 5) for task in tasks]
            avg_cognitive_load = sum(cognitive_loads) / len(cognitive_loads) if cognitive_loads else 5

            # Generate insights
            insights = {
                "user_id": str(user_id),
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": {
                    "total_tasks": total_tasks,
                    "completed_tasks": completed_tasks,
                    "overdue_tasks": overdue_tasks,
                    "completion_rate": round(completion_rate, 2),
                    "avg_cognitive_load": round(avg_cognitive_load, 2)
                },
                "insights": [
                    {
                        "type": "completion_trend",
                        "message": f"Your task completion rate is {round(completion_rate, 2)}%.",
                        "action": "Consider breaking down tasks into smaller pieces" if completion_rate < 50 else "Great job keeping up with your tasks!"
                    },
                    {
                        "type": "cognitive_load",
                        "message": f"Your average task difficulty is {round(avg_cognitive_load, 2)}/10.",
                        "action": "Consider mixing in some easier tasks" if avg_cognitive_load > 7 else "You have a good balance of task difficulty"
                    },
                    {
                        "type": "overdue",
                        "message": f"You have {overdue_tasks} overdue tasks.",
                        "action": "Review and reschedule these tasks" if overdue_tasks > 0 else "All tasks are on schedule!"
                    }
                ],
                "recommendations": self._generate_recommendations(tasks)
            }

            self.logger.info(f"Insights generated for user {user_id}")
            return insights

        except Exception as e:
            self.logger.error(f"Error generating insights for user {user_id}: {str(e)}", exc_info=True)
            raise

    def _generate_recommendations(self, tasks: List[TaskModel]) -> List[Dict[str, str]]:
        """Generate task recommendations based on analysis."""
        recommendations = []

        # Check for high number of overdue tasks
        overdue_count = sum(1 for task in tasks if task.due_date and task.due_date < datetime.utcnow() and task.status != "COMPLETED")
        if overdue_count > 3:
            recommendations.append({
                "type": "scheduling",
                "message": "You have several overdue tasks. Consider scheduling a dedicated time block to address them.",
                "priority": "high"
            })

        # Check for tasks with approaching deadlines
        soon_due = [task for task in tasks if task.due_date and
                    task.due_date > datetime.utcnow() and
                    task.due_date < datetime.utcnow() + timedelta(days=2) and
                    task.status != "COMPLETED"]

        if soon_due:
            recommendations.append({
                "type": "upcoming",
                "message": f"You have {len(soon_due)} tasks due in the next 48 hours. Prioritize these in your schedule.",
                "priority": "high"
            })

        # Check for high cognitive load days
        # This would require more date-based analysis in a real implementation

        # General recommendations
        if len(tasks) > 10 and len([t for t in tasks if t.status != "COMPLETED"]) > 7:
            recommendations.append({
                "type": "workload",
                "message": "Your current task list is quite large. Consider using the Eisenhower Matrix to prioritize.",
                "priority": "medium"
            })

        return recommendations[:3]  # Limit to top 3 recommendations

    async def health_check(self) -> Dict[str, Any]:
        """Enhanced health check implementation."""
        # Get base health check
        base_health = await super().health_check()

        # Add service-specific health information
        health_info = {
            "service": self.__class__.__name__,
            "status": base_health["status"],
            "details": {
                **base_health["details"],
                "llm_service_available": self.llm_service is not None,
                "circuit_breaker_status": {
                    "task_analysis": self._get_circuit_state("task_analysis")
                }
            }
        }

        return health_info
