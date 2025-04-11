"""Task service module."""

import logging
from datetime import datetime, date, timezone, timedelta
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from sqlalchemy import and_, asc, desc, func, select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.services.base_service import BaseService, OPEN, CLOSED, HALF_OPEN
from app.models.task_model import TaskModel, TaskPriority
from app.schemas.task_schema import TaskResponse, TaskCreate, TaskStatsSchema, TaskUpdate
from app.models.enums_model import (
    TaskStatus as TaskStatusSchema,
    BlockPriority as TaskPrioritySchema,
    TaskCategory,
    TaskState,
)
from app.utils.decorators import handle_service_error
from app.services.task_analyzer_service import TaskAnalyzerService

logger = logging.getLogger(__name__)


class TaskService(BaseService[TaskModel, TaskResponse, TaskCreate]):
    """Service for managing tasks."""

    def __init__(self, db: AsyncSession):
        """Initialize the service with database session."""
        super().__init__(db=db, model=TaskModel, schema_class=TaskResponse)
        self.analyzer = TaskAnalyzerService(db)
        # Initialize bulkhead for task analysis
        self._task_analysis_bulkhead = self.with_bulkhead(
            name="task_analysis", max_concurrent_calls=5, max_queue_size=10
        )

    @handle_service_error
    @BaseService.with_retry(
        max_retries=3,
        initial_delay=0.1,
        max_delay=1.0,
        backoff_factor=2.0,
        error_message="Failed to create task",
    )
    @BaseService.with_circuit_breaker(name="task_create", failure_threshold=5, recovery_timeout=30)
    async def create_task(self, task_data: TaskCreate) -> TaskModel:
        """Create a new task with resilience patterns."""
        logger.info(f"Creating new task with data: {task_data}")
        try:
            # Convert TaskCreate to dict and extract user_id
            task_dict = task_data.dict()
            user_id = task_dict.pop("user_id", None)
            if not user_id:
                raise HTTPException(status_code=400, detail="Missing required field: user_id")

            # Add user_id back to the dict for model creation
            task_dict["user_id"] = user_id

            # Validate fields
            required_fields = ["title"]
            for field in required_fields:
                if field not in task_dict or not task_dict[field]:
                    raise HTTPException(status_code=400, detail=f"Missing required field: {field}")

            if "status" in task_dict:
                try:
                    if isinstance(task_dict["status"], str):
                        task_dict["status"] = task_dict["status"].lower()
                    TaskStatusSchema(task_dict["status"])
                except ValueError:
                    raise ValueError(f"Invalid task status: {task_dict['status']}")

            if "priority" in task_dict:
                try:
                    if isinstance(task_dict["priority"], str):
                        task_dict["priority"] = task_dict["priority"].lower()
                    TaskPrioritySchema(task_dict["priority"])
                except ValueError:
                    raise ValueError(f"Invalid task priority: {task_dict['priority']}")

            if "estimated_duration" in task_dict:
                if (
                    not isinstance(task_dict["estimated_duration"], (int, float))
                    or task_dict["estimated_duration"] <= 0
                ):
                    raise ValueError("Estimated duration must be a positive number")

            if "due_date" in task_dict and task_dict["due_date"]:
                if not isinstance(task_dict["due_date"], datetime):
                    raise ValueError("Invalid due_date format")

            task = self.model(**task_dict)
            self.db.add(task)
            await self.db.commit()
            await self.db.refresh(task)
            logger.info(f"Successfully created task with ID: {task.id}")
            return task
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}", exc_info=True)
            await self.db.rollback()
            raise

    # Add bulkhead pattern for task analysis
    async def bulkhead_task_analysis(self, task_id: UUID) -> Dict[str, Any]:
        """
        Analyze a task with bulkhead pattern to isolate resource usage.

        Args:
            task_id: The ID of the task to analyze

        Returns:
            Dict containing analysis results
        """
        logger.info(f"Analyzing task {task_id} with bulkhead isolation")

        # Define the operation to perform inside the bulkhead
        async def analyze_operation():
            task = await self.get_by_id(task_id)
            if not task:
                raise ValueError(f"Task not found: {task_id}")

            # Call the task analyzer service
            analysis_result = await self.analyzer.analyze_task(task)
            return analysis_result

        # Execute with bulkhead isolation
        try:
            result = await self._task_analysis_bulkhead(analyze_operation)()
            logger.info(f"Task analysis completed for task {task_id}")
            return result
        except Exception as e:
            logger.error(f"Error in bulkhead_task_analysis: {str(e)}", exc_info=True)
            raise

    @handle_service_error
    @BaseService.with_retry(
        max_retries=3, initial_delay=0.1, max_delay=1.0, error_message="Failed to get user tasks"
    )
    async def get_user_tasks(
        self,
        user_id: str,
        status: Optional[TaskStatusSchema] = None,
        priority: Optional[TaskPrioritySchema] = None,
        due_before: Optional[datetime] = None,
        due_after: Optional[datetime] = None,
        completed: Optional[bool] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = "asc",
    ) -> List[TaskModel]:
        """Get all tasks for a specific user with resilience patterns."""
        logger.info(f"Fetching tasks for user {user_id} from database")
        try:
            query = select(self.model).where(self.model.user_id == user_id)
            if status:
                query = query.where(self.model.status == status)
            if priority:
                query = query.where(self.model.priority == priority)
            if due_before:
                if due_before.tzinfo is None:
                    due_before = due_before.replace(tzinfo=timezone.utc)
                start_of_day = due_before.replace(hour=0, minute=0, second=0, microsecond=0)
                query = query.where(
                    and_(
                        self.model.due_date.isnot(None),
                        self.model.due_date < start_of_day,
                    )
                )
            if due_after:
                if due_after.tzinfo is None:
                    due_after = due_after.replace(tzinfo=timezone.utc)
                end_of_day = due_after.replace(hour=23, minute=59, second=59, microsecond=999999)
                query = query.where(
                    and_(
                        self.model.due_date.isnot(None),
                        self.model.due_date > end_of_day,
                    )
                )
            if completed is not None:
                query = query.where(self.model.completed == completed)
            if sort_by:
                sort_column = getattr(self.model, sort_by, None)
                if sort_column is None:
                    raise ValueError(f"Invalid sort column: {sort_by}")
                if sort_order.lower() == "desc":
                    query = query.order_by(desc(sort_column))
                else:
                    query = query.order_by(asc(sort_column))
            result = await self.db.execute(query)
            tasks = list(result.scalars().all())
            logger.info(f"Found {len(tasks)} tasks for user {user_id}")
            return tasks
        except Exception as e:
            logger.error(f"Error fetching tasks for user {user_id}: {str(e)}", exc_info=True)
            raise

    @handle_service_error
    @BaseService.with_retry(
        max_retries=2, initial_delay=0.1, error_message="Failed to get task by ID"
    )
    async def get_task(self, task_id: UUID, user_id: UUID) -> Optional[TaskModel]:
        """Get a specific task by ID."""
        task = await self.get_by_id(task_id)
        if task and task.user_id == user_id:
            return task
        return None

    @handle_service_error
    @BaseService.with_retry(max_retries=3, initial_delay=0.1, error_message="Failed to update task")
    @BaseService.with_circuit_breaker(name="task_update", failure_threshold=5, recovery_timeout=30)
    async def update_task(self, task_id: UUID, update_data: Dict[str, Any]) -> TaskModel:
        """Update a task with resilience patterns."""
        task = await self.get_task(task_id, task_id)
        if not task:
            raise ValueError(f"Task with id {task_id} not found")
        if "priority" in update_data:
            if isinstance(update_data["priority"], str):
                update_data["priority"] = TaskPrioritySchema[update_data["priority"]]
            elif isinstance(update_data["priority"], int):
                update_data["priority"] = TaskPrioritySchema(update_data["priority"])
        if "status" in update_data and update_data["status"] == TaskStatusSchema.COMPLETED:
            update_data["completion_date"] = datetime.now(timezone.utc)
            update_data["completed"] = True
        for key, value in update_data.items():
            setattr(task, key, value)
        task.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(task)
        return task

    @handle_service_error
    @BaseService.with_retry(max_retries=3, initial_delay=0.1, error_message="Failed to delete task")
    async def delete_task(self, task_id: UUID, user_id: UUID) -> bool:
        """Delete a task."""
        task = await self.get_task(task_id, user_id)
        if not task:
            return False
        await self.db.delete(task)
        await self.db.commit()
        return True

    @handle_service_error
    @BaseService.with_retry(
        max_retries=3, initial_delay=0.1, error_message="Failed to complete task"
    )
    async def complete_task(self, task_id: UUID, user_id: UUID) -> Optional[TaskModel]:
        """Mark a task as completed."""
        logger.info(f"Marking task {task_id} as complete")
        try:
            task = await self.get_task(task_id, user_id)
            if not task:
                logger.warning(f"Task {task_id} not found")
                raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
            task.completed = True
            task.completed_at = datetime.now(timezone.utc)
            await self.db.commit()
            await self.db.refresh(task)
            return task
        except Exception as e:
            logger.error(f"Error completing task {task_id}: {str(e)}")
            await self.db.rollback()
            raise

    @handle_service_error
    @BaseService.with_retry(
        max_retries=2, initial_delay=0.1, error_message="Failed to get task statistics"
    )
    async def get_task_statistics(self, user_id: UUID) -> Dict[str, Any]:
        """Get statistics about tasks for a user."""
        # Count tasks by status
        status_counts = {}
        for status in TaskStatus:
            query = select(func.count()).where(
                and_(self.model.user_id == user_id, self.model.status == status)
            )
            result = await self.db.execute(query)
            status_counts[status.value] = result.scalar() or 0

        # Count overdue tasks
        now = datetime.now()
        overdue_query = select(func.count()).where(
            and_(
                self.model.user_id == user_id,
                self.model.due_date < now,
                self.model.status != TaskStatus.COMPLETED,
            )
        )
        overdue_result = await self.db.execute(overdue_query)
        overdue_count = overdue_result.scalar() or 0

        # Count tasks due today
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        today_query = select(func.count()).where(
            and_(
                self.model.user_id == user_id,
                self.model.due_date >= today_start,
                self.model.due_date < today_end,
                self.model.status != TaskStatus.COMPLETED,
            )
        )
        today_result = await self.db.execute(today_query)
        today_count = today_result.scalar() or 0

        # Get completion rate
        total_query = select(func.count()).where(self.model.user_id == user_id)
        total_result = await self.db.execute(total_query)
        total_count = total_result.scalar() or 0

        completed_count = status_counts.get(TaskStatus.COMPLETED.value, 0)
        completion_rate = (completed_count / total_count) * 100 if total_count > 0 else 0

        return {
            "status_counts": status_counts,
            "overdue_count": overdue_count,
            "due_today": today_count,
            "total_count": total_count,
            "completed_count": completed_count,
            "completion_rate": round(completion_rate, 2),
        }

    async def health_check(self) -> Dict[str, Any]:
        """Get the health status of the task service."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        analyzer_health = await self._get_analyzer_health()
        circuit_states = {
            "task_create": self._get_circuit_state("task_create"),
            "task_update": self._get_circuit_state("task_update"),
        }

        # Get bulkhead state
        bulkhead_state = {
            "task_analysis": {
                "max_concurrent": 5,  # From initialization
                "max_queue": 10,  # From initialization
            }
        }

        # Determine overall health based on circuits
        is_healthy = all(state == CLOSED for state in circuit_states.values())
        analyzer_is_healthy = analyzer_health.get("status") == "healthy"

        return {
            "service": "TaskService",
            "status": "healthy" if (is_healthy and analyzer_is_healthy) else "degraded",
            "timestamp": now,
            "details": {
                "circuits": circuit_states,
                "bulkheads": bulkhead_state,
                "analyzer": analyzer_health,
            },
        }

    def _get_analyzer_health(self) -> Dict[str, Any]:
        """Get health status of analyzer service."""
        # In a real implementation, this would check the actual service
        analyzer_circuit = self._get_circuit_state("task_analyzer")
        return {
            "status": (
                "healthy"
                if analyzer_circuit == CLOSED
                else "degraded" if analyzer_circuit == HALF_OPEN else "unhealthy"
            ),
            "circuit": analyzer_circuit,
        }

    def _get_circuit_state(self, circuit_name: str) -> str:
        """Get the current state of a circuit breaker.

        This is a helper method that would need to access circuit breaker state.
        For a real implementation, this would need access to the circuit breaker object.
        """
        # In a real implementation, this would access the circuit breaker object
        # For now, we'll assume closed (healthy) state
        return CLOSED

    def create_task(self, task: TaskCreate, user_id: str) -> TaskModel:
        """Create a new task with proper state initialization."""
        db_task = self.model(
            user_id=user_id,
            title=task.title,
            description=task.description,
            due_date=task.due_date,
            estimated_duration=task.estimated_duration,
            priority=task.priority,
            difficulty=task.difficulty,
            energy_required=task.energy_required,
            focus_required=task.focus_required,
            status=TaskState.TODO.value,  # Initialize with TODO state
        )
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        return db_task

    def update_task_status(
        self, task_id: str, new_status: str, user_id: str
    ) -> Optional[TaskModel]:
        """Update task status with validation."""
        task = (
            self.db.query(self.model)
            .filter(self.model.id == task_id, self.model.user_id == user_id)
            .first()
        )

        if not task:
            return None

        if task.update_status(new_status):
            self.db.commit()
            self.db.refresh(task)
            return task
        return None

    def get_task(self, task_id: str, user_id: str) -> Optional[TaskModel]:
        """Get a task by ID with next states."""
        task = (
            self.db.query(self.model)
            .filter(self.model.id == task_id, self.model.user_id == user_id)
            .first()
        )

        if task:
            task.next_states = task.get_next_states()
        return task

    def get_user_tasks(self, user_id: str) -> List[TaskModel]:
        """Get all tasks for a user with next states."""
        tasks = self.db.query(self.model).filter(self.model.user_id == user_id).all()

        for task in tasks:
            task.next_states = task.get_next_states()
        return tasks

    def update_task(
        self, task_id: str, task_update: TaskUpdate, user_id: str
    ) -> Optional[TaskModel]:
        """Update task with status transition validation."""
        task = (
            self.db.query(self.model)
            .filter(self.model.id == task_id, self.model.user_id == user_id)
            .first()
        )

        if not task:
            return None

        # Handle status update separately if provided
        if task_update.status and task_update.status != task.status:
            if not task.update_status(task_update.status):
                return None

        # Update other fields
        for field, value in task_update.dict(exclude={"status"}).items():
            if value is not None:
                setattr(task, field, value)

        self.db.commit()
        self.db.refresh(task)
        task.next_states = task.get_next_states()
        return task

    def delete_task(self, task_id: str, user_id: str) -> bool:
        """Delete a task."""
        task = (
            self.db.query(self.model)
            .filter(self.model.id == task_id, self.model.user_id == user_id)
            .first()
        )

        if task:
            self.db.delete(task)
            self.db.commit()
            return True
        return False
