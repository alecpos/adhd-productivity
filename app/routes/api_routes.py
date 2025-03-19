from app.routes.body_doubling import body_doubling_router
from fastapi import APIRouter, Depends, HTTPException
from fastapi.logger import logger
from app.schemas.task_schema import TaskResponse, TaskCreate
from app.services.scheduling_service import SchedulingService
router = APIRouter(prefix="/api/v1")

# Include sub-routers
router.include_router(body_doubling_router)


@router.post(
    "/tasks/",
    response_model=TaskResponse,
    summary="Create a new task",
    description="Create a new task with energy level consideration",
)
async def create_task(
    task: TaskCreate, scheduling_service: SchedulingService = Depends()
) -> TaskResponse:
    try:
        result = await scheduling_service.schedule_task(task.dict())
        return TaskResponse(**result)
    except Exception as e:
        logger.error(f"Error in API router: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while creating task")
