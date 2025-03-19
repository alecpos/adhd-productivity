from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user_model import User
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("/statistics", response_model=TaskStatisticsResponse)
async def get_task_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get task statistics for the current user."""
    try:
        service = TaskService(db)
        tasks = await service.get_user_tasks(current_user.id)
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.completed])
        pending_tasks = total_tasks - completed_tasks
        return TaskStatisticsResponse(
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            pending_tasks=pending_tasks,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
