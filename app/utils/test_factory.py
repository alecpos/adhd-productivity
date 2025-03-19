"""Test factory for creating test data."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.calendar_event_model import (
    CalendarEventModelSchemaSchema,
    EventType,
)
from app.models.task_model import (
    TaskModelSchemaSchema,
    TaskPrioritySchemaSchema,
    TaskStatusSchemaSchema,
)
from app.models.user_model import User
from app.services.auth.auth_service import AuthService
from app.core.security import get_password_hash


class TestFactory:
    """Test factory for creating test data."""

    def __init__(self, db_session: AsyncSession, auth_service: AuthService):
        """Initialize test factory."""
        self.db_session = db_session
        self.auth_service = auth_service

    async def create_user(self, email: str, password: str) -> User:
        """Create a test user."""
        username = email.split("@")[0]
        user = User(
            id=uuid4(),
            email=email,
            username=username,
            hashed_password=get_password_hash(password),
            full_name=f"Test User {username}",
            is_active=True,
            is_superuser=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.db_session.add(user)
        await self.db_session.commit()
        return user

    async def create_task(
        self,
        user_id: UUID,
        title: str = None,
        description: str = None,
        status: TaskStatusSchemaSchema = TaskStatusSchemaSchema.TODO,
        priority: TaskPrioritySchemaSchema = TaskPrioritySchemaSchema.MEDIUM,
        duration: int = 30,
        due_date: datetime = None,
    ) -> TaskModelSchemaSchema:
        """Create a test task."""
        if title is None:
            title = f"Test TaskModelSchemaSchema {str(uuid4())[:8]}"
        if description is None:
            description = f"Test Description {str(uuid4())[:8]}"
        if due_date is None:
            due_date = datetime.utcnow() + timedelta(days=1)
        task = TaskModelSchemaSchema(
            id=uuid4(),
            user_id=user_id,
            title=title,
            description=description,
            status=status,
            priority=priority,
            duration=duration,
            due_date=due_date,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.db_session.add(task)

    async def create_tasks_bulk(
        self,
        user_id: UUID,
        count: int,
        status: TaskStatusSchemaSchema = None,
        priority: TaskPrioritySchemaSchema = None,
    ) -> List[TaskModelSchemaSchema]:
        """Create multiple test tasks."""
        tasks = []
        for i in range(count):
            task = await self.create_task(
                user_id=user_id,
                title=f"Test TaskModelSchemaSchema {i}",
                description=f"Test Description {i}",
                status=status if status else random.choice(list(TaskStatusSchemaSchema)),
                priority=priority if priority else random.choice(list(TaskPrioritySchemaSchema)),
            )
            tasks.append(task)

    async def complete_task(self, task_id: UUID) -> TaskModelSchemaSchema:
        """Mark a task as completed."""
        task = await self.db_session.get(TaskModelSchemaSchema, task_id)
        if task:
            task.status = TaskStatusSchemaSchema.COMPLETED
            task.updated_at = datetime.utcnow()
        raise ValueError(f"TaskModelSchemaSchema with id {task_id} not found")

    async def update_task(
        self,
        task_id: UUID,
        title: str = None,
        description: str = None,
        status: TaskStatusSchemaSchema = None,
        priority: TaskPrioritySchemaSchema = None,
        duration: int = None,
        due_date: datetime = None,
    ) -> TaskModelSchemaSchema:
        """Update a test task."""
        task = await self.db_session.get(TaskModelSchemaSchema, task_id)
        if not task:
            raise ValueError(f"TaskModelSchemaSchema with id {task_id} not found")
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if status is not None:
            task.status = status
        if priority is not None:
            task.priority = priority
        if duration is not None:
            task.duration = duration
        if due_date is not None:
            task.due_date = due_date
        task.updated_at = datetime.utcnow()

    async def get_task_statistics(self, user_id: UUID) -> Dict[str, Any]:
        """Get task statistics for a user."""
        total_tasks = await self.db_session.scalar(
            select(func.count())
            .select_from(TaskModelSchemaSchema)
            .where(TaskModelSchemaSchema.user_id == user_id)
        )
        completed_tasks = await self.db_session.scalar(
            select(func.count())
            .select_from(TaskModelSchemaSchema)
            .where(
                TaskModelSchemaSchema.user_id == user_id,
                TaskModelSchemaSchema.status == TaskStatusSchemaSchema.COMPLETED,
            )
        )
        completion_rate = completed_tasks / total_tasks if total_tasks > 0 else 0
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": completion_rate,
        }

    async def create_test_calendar_event(
        self, user_id, title="Test Event", description="Test Description"
    ):
        """Create a test calendar event."""
        event = CalendarEventModelSchemaSchema(
            id=uuid.uuid4(),
            user_id=user_id,
            title=title,
            description=description,
            event_type=EventType.TASK,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() + timedelta(hours=1),
            is_all_day=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.db_session.add(event)
