"""Block scheduler routes module."""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.database import get_db
from app.models.user_model import User
from app.schemas.scheduling_schema import (
    TimeBlockInput,
    OptimizeScheduleRequest,
    ScheduleParams,
    ScheduleOptimizer,
)
from app.services.schedule_optimizer_service import ScheduleOptimizerService
from app.services.service_factory_service import ServiceFactory
from app.utils.exceptions import AuthenticationError

logger = logging.getLogger(__name__)
router = APIRouter()


def ensure_timezone_aware(dt: datetime) -> datetime:
    """Ensure datetime is timezone-aware, using UTC if naive."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def get_optimizer_service(db: AsyncSession = Depends(get_db)) -> ScheduleOptimizerService:
    """Get optimizer service instance."""
    return ServiceFactory().get_schedule_optimizer_service(db)


def create_success_response(data: Any) -> Dict[str, Any]:
    """Create a standardized success response."""
    return {"success": True, "data": data}


def create_error_response_dict(
    code: str, message: str, details: Optional[Dict] = None
) -> Dict[str, Any]:
    """Create a standardized error response dictionary."""
    return {"success": False, "error": {"code": code, "message": message, "details": details}}


@router.post("/blocks")
async def schedule_blocks(
    request: Request,
    user_id: str,
    start_date: datetime,
    end_date: datetime,
    focus_time: int = 25,
    break_time: int = 5,
    long_break_time: int = 15,
    blocks_before_long_break: int = 4,
    preferred_hours: Optional[List[int]] = None,
    energy_based_scheduling: bool = True,
    mental_health_aware: bool = True,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """Schedule blocks for a user."""
    try:
        if current_user.id != user_id:
            raise AuthenticationError("User not authorized to access this resource")

        start_date = ensure_timezone_aware(start_date)
        end_date = ensure_timezone_aware(end_date)

        optimizer_service = get_optimizer_service(db)
        await optimizer_service.initialize()

        optimal_schedule = await get_optimal_schedule(start_date, end_date, optimizer_service)
        return JSONResponse(content=create_success_response(optimal_schedule.dict()))

    except AuthenticationError as e:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=create_error_response_dict("AUTH_ERROR", str(e)),
        )
    except Exception as e:
        logger.error(f"Error scheduling blocks: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=create_error_response_dict("SCHEDULE_ERROR", str(e)),
        )


@router.get("/stats")
async def get_schedule_stats(
    request: Request,
    current_user: User = Depends(get_current_user),
    optimizer_service: ScheduleOptimizerService = Depends(get_optimizer_service),
) -> JSONResponse:
    """Get schedule statistics for the current user."""
    try:
        await optimizer_service.initialize()
        stats = await optimizer_service.get_schedule_stats(current_user.id)
        return JSONResponse(content=create_success_response(stats))
    except Exception as e:
        logger.error(f"Error getting schedule stats: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=create_error_response_dict("STATS_ERROR", str(e)),
        )


@router.post("/optimize")
async def optimize_schedule(
    request: Request,
    schedule_request: OptimizeScheduleRequest,
    current_user: User = Depends(get_current_user),
    optimizer_service: ScheduleOptimizerService = Depends(get_optimizer_service),
) -> JSONResponse:
    """Optimize schedule based on request parameters."""
    try:
        await optimizer_service.initialize()
        optimized_schedule = await optimizer_service.optimize_schedule(
            current_user.id,
            schedule_request.tasks,
            schedule_request.date,
            schedule_request.work_hours,
            schedule_request.energy_pattern,
        )
        return JSONResponse(content=create_success_response(optimized_schedule))
    except Exception as e:
        logger.error(f"Error optimizing schedule: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=create_error_response_dict("OPTIMIZE_ERROR", str(e)),
        )


@router.get("/optimizer")
async def get_schedule_optimizer(
    request: Request,
    start_date: datetime,
    end_date: datetime,
    timezone: str,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """Get schedule optimizer service."""
    try:
        optimizer_service = get_optimizer_service(db)
        optimizer = await optimizer_service.get_optimizer(start_date, end_date, timezone)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=create_success_response(optimizer),
        )
    except AuthenticationError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=create_error_response_dict("authentication_error", "Unauthorized"),
        )
    except Exception as e:
        logger.error(f"Error getting schedule optimizer: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=create_error_response_dict("optimizer_error", str(e)),
        )


async def get_schedule_status(request_id: str) -> JSONResponse:
    """Get status of schedule optimization request."""
    try:
        # Add delay to simulate processing
        await asyncio.sleep(1)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=create_success_response({"status": "processing"}),
        )
    except Exception as e:
        logger.error(f"Error getting schedule status: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=create_error_response_dict("status_error", str(e)),
        )


async def get_optimal_schedule(
    start_date: datetime,
    end_date: datetime,
    optimizer_service: ScheduleOptimizerService = Depends(get_optimizer_service),
) -> TimeBlockInput:
    """Get optimal schedule for given date range."""
    await optimizer_service.initialize()
    return await optimizer_service.get_optimal_schedule(start_date, end_date)
