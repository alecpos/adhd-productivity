import logging
from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.auth_service import get_current_user
from app.schemas.energy_schema import (
    EnergyPatternsSchema,
    EnergyLogCreateSchema,
    EnergyLogResponseSchema,
)
from app.services.energy_service import EnergyService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/energy-mapping", tags=["energy"])


@router.get("/patterns", response_model=EnergyPatternsSchema)
async def get_energy_patterns(
    current_user: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get energy patterns for the current user."""
    logger.info(f"Fetching energy patterns for user: {current_user}")
    try:
        energy_service = EnergyService(db)
        patterns = await energy_service.get_energy_patterns(current_user)
        logger.info(f"Successfully retrieved energy patterns for user: {current_user}")
        return patterns
    except Exception as e:
        logger.error(f"Error getting energy patterns: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get energy patterns: {str(e)}",
        )


@router.post("/log", response_model=EnergyLogResponseSchema)
async def log_energy_level(
    log_data: EnergyLogCreateSchema,
    current_user: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Log energy level for the current user."""
    logger.info(f"Logging energy level for user: {current_user}")
    try:
        energy_service = EnergyService(db)
        log = await energy_service.log_energy_level(
            user_id=current_user,
            energy_level=log_data.energy_level,
            activity=log_data.activity,
            notes=log_data.notes,
            timestamp=log_data.timestamp,
        )
        logger.info(f"Successfully logged energy level for user: {current_user}")
        return log
    except Exception as e:
        logger.error(f"Error logging energy level: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to log energy level: {str(e)}",
        )


@router.get("/logs", response_model=List[EnergyLogResponseSchema])
async def get_energy_logs(
    current_user: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all energy logs for the current user."""
    logger.info(f"Fetching energy logs for user: {current_user}")
    try:
        energy_service = EnergyService(db)
        logs = await energy_service.get_user_logs(current_user)
        logger.info(f"Successfully retrieved {len(logs)} energy logs for user: {current_user}")
        return logs
    except Exception as e:
        logger.error(f"Error getting energy logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get energy logs: {str(e)}",
        )
