from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from uuid import UUID
from datetime import datetime

from app.database import get_db
from app.schemas.task_schema import TaskSchema, TaskCreate, TaskUpdate, TaskResponseSchema

finance_router = APIRouter()


async def get_db_session(session: AsyncSession = Depends(get_db)) -> AsyncSession:
    return session


@finance_router.post(
    "/tasks",
    response_model=TaskResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
)
async def create_task(task_data: TaskCreate, db: AsyncSession = Depends(get_db_session)):
    """
    Create a new task for a user.
    """
    try:
        new_task = TaskSchema(
            title=task_data.title,
            description=task_data.description,
            completed=task_data.completed or False,
            due_date=datetime.strptime(task_data.due_date, "%Y-%m-%d"),
            user_id=task_data.user_id,
        )
        db.add(new_task)
        await db.commit()
        await db.refresh(new_task)
        return TaskResponseSchema(
            id=new_task.id,
            title=new_task.title,
            description=new_task.description,
            completed=new_task.completed,
            due_date=new_task.due_date,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating task: {str(e)}",
        )


@finance_router.get(
    "/tasks/{user_id}", response_model=list[TaskResponseSchema], summary="Get tasks for a user"
)
async def get_tasks(user_id: UUID, db: AsyncSession = Depends(get_db_session)):
    """
    Retrieve all tasks for a given user.
    """
    result = await db.execute(select(TaskSchema).where(TaskSchema.user_id == user_id))
    tasks = result.scalars().all()
    if not tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No tasks found for this user."
        )
    return [
        TaskResponseSchema(
            id=task.id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            due_date=task.due_date,
        )
        for task in tasks
    ]


@finance_router.put(
    "/tasks/{task_id}", response_model=TaskResponseSchema, summary="Update an existing task"
)
async def update_task(
    task_id: int, task_data: TaskUpdate, db: AsyncSession = Depends(get_db_session)
):
    """
    Update details of an existing task.
    """
    result = await db.execute(select(TaskSchema).where(TaskSchema.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TaskSchema not found.")
    for field, value in task_data.dict(exclude_unset=True).items():
        setattr(task, field, value)
    await db.commit()
    await db.refresh(task)
    return TaskResponseSchema(
        id=task.id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        due_date=task.due_date,
    )


@finance_router.delete(
    "/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a task"
)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db_session)):
    """
    Delete a task by its ID.
    """
    result = await db.execute(select(TaskSchema).where(TaskSchema.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TaskSchema not found.")
    await db.delete(task)
    await db.commit()
    return {"message": "TaskSchema deleted successfully."}
