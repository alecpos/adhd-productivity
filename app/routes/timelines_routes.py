from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

timeline_router = APIRouter(
    prefix="/timelines",
    tags=["Timelines"],
    responses={404: {"description": "Not Found"}},
)


async def get_timeline_service(db: AsyncSession = Depends(get_db)):
    return TimelineService(db=db)


@timeline_router.post(
    "/add",
    response_model=TimelineEventResponse,
    summary="Add a Timeline Event",
    description="Add a task or subscription event to the timeline.",
)
async def add_timeline_event(
    request: TimelineEventCreate,
    service: TimelineService = Depends(get_timeline_service),
):
    try:
        event = await service.add_event(request)
        return {
            "success": True,
            "message": "Timeline event added successfully.",
            "data": event,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding timeline event: {str(e)}")


@timeline_router.get(
    "/filtered",
    response_model=FilteredTimelineResponse,
    summary="Get Filtered Timeline",
    description="Retrieve filtered timeline events by type and/or date range.",
)
async def get_filtered_timeline(
    user_id: UUID,
    event_type: Optional[str] = Query(
        None, description="Filter by event type (task or subscription)"
    ),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    service: TimelineService = Depends(get_timeline_service),
):
    try:
        timeline = await service.get_filtered_timeline(user_id, event_type, start_date, end_date)
        return {
            "success": True,
            "message": "Filtered timeline retrieved successfully.",
            "data": timeline,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving filtered timeline: {str(e)}")
