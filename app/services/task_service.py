"""Task service module."""

import logging
from datetime import datetime, date, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import and_, asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.services.base_service import BaseService
from app.models.task_model import TaskModel
from app.schemas.task_schema import TaskResponse, TaskCreate, TaskStatsSchema
from app.models.enums_model import TaskStatus as TaskStatusSchema, BlockPriority as TaskPrioritySchema
from app.models.task_category_model import TaskCategoryModel as TaskCategory
from app.utils.decorators import handle_service_error

logger = logging.getLogger(__name__)


class TaskService(BaseService[TaskModel, TaskResponse, TaskCreate]):
    """Service for managing tasks."""

    def __init__(self, db: AsyncSession):
        """Initialize the service with database session."""
        super().__init__(db=db, model=TaskModel, schema_class=TaskResponse)

    @handle_service_error
    async def create_task(self, task_data: dict) -> TaskModel:
        """Create a new task."""
        logger.info(f"Creating new task with data: {task_data}")
        try:
            required_fields = ["title", "user_id"]
            for field in required_fields:
                if field not in task_data or not task_data[field]:
                    raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
            if "status" in task_data:
                try:
                    if isinstance(task_data["status"], str):
                        task_data["status"] = task_data["status"].lower()
                    TaskStatusSchema(task_data["status"])
                except ValueError:
                    raise ValueError(f"Invalid task status: {task_data['status']}")
            if "priority" in task_data:
                try:
                    if isinstance(task_data["priority"], str):
                        task_data["priority"] = task_data["priority"].lower()
                    TaskPrioritySchema(task_data["priority"])
                except ValueError:
                    raise ValueError(f"Invalid task priority: {task_data['priority']}")
            if "estimated_duration" in task_data:
                if (
                    not isinstance(task_data["estimated_duration"], (int, float))
                    or task_data["estimated_duration"] <= 0
                ):
                    raise ValueError("Estimated duration must be a positive number")
            if "due_date" in task_data and task_data["due_date"]:
                if not isinstance(task_data["due_date"], datetime):
                    raise ValueError("Invalid due_date format")
            task = self.model(**task_data)
            self.db.add(task)
            await self.db.commit()
            await self.db.refresh(task)
            logger.info(f"Successfully created task with ID: {task.id}")
            return task
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}", exc_info=True)
            raise

    @handle_service_error
    async def update_task(self, task_id: UUID, update_data: Dict[str, Any]) -> TaskModel:
        """Update a task."""
        task = await self.get_by_id(task_id)
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
        """Get all tasks for a specific user with filtering and sorting."""
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
    async def complete_task(self, task_id: str) -> Optional[TaskModel]:
        """Mark a task as complete."""
        logger.info(f"Marking task {task_id} as complete")
        try:
            task = await self.get_by_id(task_id)
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
            raise

    @handle_service_error
    async def get_statistics(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get task statistics."""
        logger.info(f"Calculating task statistics (start_date: {start_date}, end_date: {end_date})")
        try:
            conditions = []
            if start_date:
                conditions.append(self.model.created_at >= start_date)
            if end_date:
                conditions.append(self.model.created_at <= end_date)
            total_query = select(func.count()).select_from(self.model)
            if conditions:
                total_query = total_query.where(and_(*conditions))
            total_result = await self.db.execute(total_query)
            total_tasks = total_result.scalar()
            completed_conditions = conditions + [self.model.completed == True]
            completed_query = (
                select(func.count()).select_from(self.model).where(and_(*completed_conditions))
            )
            completed_result = await self.db.execute(completed_query)
            completed_tasks = completed_result.scalar()
            stats = {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "completion_rate": completed_tasks / total_tasks * 100 if total_tasks > 0 else 0,
            }
            logger.info(f"Task statistics calculated: {stats}")
        except Exception as e:
            logger.error(f"Error calculating task statistics: {str(e)}", exc_info=True)

    @handle_service_error
    async def get_overdue_tasks(self) -> List[TaskModel]:
        """Get all overdue tasks."""
        logger.info("Fetching overdue tasks from database")
        try:
            today = date.today()
            query = select(self.model).where(
                and_(self.model.due_date < today, self.model.completed == False)
            )
            result = await self.db.execute(query)
            tasks = result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching overdue tasks: {str(e)}", exc_info=True)

    @handle_service_error
    async def get_tasks_due_today(self) -> List[TaskModel]:
        """Get all tasks due today."""
        logger.info("Fetching tasks due today from database")
        try:
            today = date.today()
            query = select(self.model).where(
                and_(self.model.due_date == today, self.model.completed == False)
            )
            result = await self.db.execute(query)
            tasks = result.scalars().all()
            logger.info(f"Found {len(tasks)} tasks due today")
        except Exception as e:
            logger.error(f"Error fetching tasks due today: {str(e)}", exc_info=True)

    @handle_service_error
    async def get_task_statistics(self, user_id: str) -> TaskStatsSchema:
        """Get task statistics for a user."""
        logger.info(f"Calculating task statistics for user {user_id}")
        try:
            result = await self.db.execute(
                select(TaskModel).where(TaskModel.user_id == user_id)
            )
            tasks = result.scalars().all()
            total_tasks = len(tasks)
            completed_tasks = sum((1 for task in tasks if task.completed))
            completion_rate = completed_tasks / total_tasks if total_tasks > 0 else 0.0
            durations = [t.actual_duration for t in tasks if t.actual_duration is not None]
            average_duration = sum(durations) / len(durations) if durations else None
            energy_required = [t.energy_required for t in tasks if t.energy_required is not None]
            average_energy_required = (
                sum(energy_required) / len(energy_required) if energy_required else None
            )
            quality_scores = [t.quality_score for t in tasks if t.quality_score is not None]
            average_quality_score = (
                sum(quality_scores) / len(quality_scores) if quality_scores else None
            )
            tasks_by_category = {category: 0 for category in TaskCategory}
            for task in tasks:
                tasks_by_category[task.category] += 1
            tasks_by_priority = {priority: 0 for priority in TaskPrioritySchema}
            for task in tasks:
                tasks_by_priority[task.priority] += 1
            tasks_by_status = {status: 0 for status in TaskStatusSchema}
            for task in tasks:
                tasks_by_status[task.status] += 1
            logger.info(f"Successfully calculated task statistics for user {user_id}")
            return TaskStatsSchema(
                total_tasks=total_tasks,
                completed_tasks=completed_tasks,
                completion_rate=completion_rate,
                average_duration=average_duration,
                average_energy_required=average_energy_required,
                average_quality_score=average_quality_score,
                tasks_by_category=tasks_by_category,
                tasks_by_priority=tasks_by_priority,
                tasks_by_status=tasks_by_status,
                updated_at=datetime.now(timezone.utc),
            )
        except Exception as e:
            logger.error(f"Error calculating task statistics: {str(e)}", exc_info=True)

    @handle_service_error
    async def delete_task(self, task_id: str, user_id: str) -> bool:
        """Delete a task."""
        logger.info(f"Deleting task {task_id} for user {user_id}")
        try:
            task = await self.get_by_id(task_id)
            if not task:
                logger.warning(f"Task {task_id} not found")
            if str(task.user_id) != user_id:
                logger.warning(
                    f"User {user_id} attempted to delete task {task_id} belonging to user {task.user_id}"
                )
                raise ValueError("Cannot delete task belonging to another user")
            return await self.delete(task_id)
        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {str(e)}", exc_info=True)

    @handle_service_error
    async def get_task_by_id(self, task_id: str) -> TaskModel:
        """Get a task by its ID."""
        logger.info(f"Fetching task with ID {task_id}")
        try:
            try:
                UUID(task_id)
            except ValueError:
                raise ValueError(f"Invalid task ID format: {task_id}")
            query = select(self.model).where(self.model.id == task_id)
            result = await self.db.execute(query)
            task = result.scalar_one_or_none()
            if task is None:
                raise ValueError(f"Task not found with ID: {task_id}")
        except Exception as e:
            logger.error(f"Error fetching task {task_id}: {str(e)}", exc_info=True)

    @handle_service_error
    async def get_by_id(self, task_id: UUID) -> TaskModel:
        """Get a task by its ID."""
        logger.info(f"Fetching task with ID {task_id}")
        try:
            query = select(self.model).where(self.model.id == task_id)
            result = await self.db.execute(query)
            task = result.scalar_one_or_none()
            if task is None:
                logger.error(f"Task not found with ID: {task_id}")
                raise ValueError(f"Task not found with ID: {task_id}")
        except Exception as e:
            logger.error(f"Error fetching task {task_id}: {str(e)}")
