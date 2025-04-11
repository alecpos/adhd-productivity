"""
BioAuth-25 API endpoints

This module provides API endpoints for the BioAuth-25 wearable integration.
It allows users to register devices, get biometric data, and manage their
wearable connections according to the BioAuth-25 standard.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.bioauth_service import (
    BioAuthService,
    get_bioauth_service,
    BioAuthDeviceInfo,
    BiometricDataPoint,
    BiometricType,
    WearableDeviceType,
)
from app.core.security.security import get_current_user
from app.models.user_model import UserModel
from pydantic import BaseModel

router = APIRouter(
    prefix="/bioauth",
    tags=["bioauth"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Not authenticated"},
        status.HTTP_403_FORBIDDEN: {"description": "Not authorized to access this resource"},
        status.HTTP_404_NOT_FOUND: {"description": "Resource not found"},
    },
)


class DeviceRegistrationRequest(BaseModel):
    """Request body for device registration."""

    device_type: WearableDeviceType
    manufacturer: str
    model: str
    device_identifier: str
    auth_code: str


@router.post("/devices", response_model=BioAuthDeviceInfo)
async def register_device(
    device_data: DeviceRegistrationRequest = Body(...),
    bioauth_service: BioAuthService = Depends(get_bioauth_service),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new wearable device with BioAuth-25 protocol.

    This endpoint allows users to register their wearable devices by providing
    device information and an authorization code obtained from the device's
    pairing process.
    """
    try:
        device_info = await bioauth_service.register_device(
            user_id=str(current_user.id),
            device_type=device_data.device_type,
            manufacturer=device_data.manufacturer,
            model=device_data.model,
            device_identifier=device_data.device_identifier,
            auth_code=device_data.auth_code,
            db=db,
        )
        return device_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Device registration failed: {str(e)}"
        )


@router.get("/devices", response_model=List[BioAuthDeviceInfo])
async def get_user_devices(
    bioauth_service: BioAuthService = Depends(get_bioauth_service),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all registered wearable devices for the current user.

    Returns a list of all devices that have been registered by the user,
    including device information and connection status.
    """
    try:
        devices = await bioauth_service.get_user_devices(user_id=str(current_user.id), db=db)
        return devices
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to retrieve devices: {str(e)}"
        )


@router.get("/data/{device_id}/{metric_type}", response_model=List[BiometricDataPoint])
async def get_biometric_data(
    device_id: str,
    metric_type: BiometricType,
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    bioauth_service: BioAuthService = Depends(get_bioauth_service),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get biometric data from a specific device and metric type.

    This endpoint retrieves biometric data points for the specified device and metric,
    within the given time range. If no time range is specified, it returns the most
    recent data (last hour by default).
    """
    # Set default time range if not provided
    if end_time is None:
        end_time = datetime.utcnow()
    if start_time is None:
        start_time = end_time - timedelta(hours=1)

    try:
        data_points = await bioauth_service.get_recent_biometric_data(
            user_id=str(current_user.id),
            device_id=device_id,
            metric_type=metric_type,
            start_time=start_time,
            end_time=end_time,
            db=db,
        )
        return data_points
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to retrieve biometric data: {str(e)}",
        )


@router.post("/webhook", include_in_schema=False)
async def bioauth_webhook(
    webhook_data: Dict[str, Any] = Body(...),
    bioauth_service: BioAuthService = Depends(get_bioauth_service),
):
    """
    Webhook endpoint for BioAuth-25 device notifications.

    This endpoint receives webhook notifications from BioAuth-25 compatible devices
    and services. It processes data updates, status changes, and other notifications.

    Note: This endpoint is not authenticated as it's called by external services
    with their own authentication mechanisms (signatures).
    """
    try:
        result = await bioauth_service.process_webhook(webhook_data)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Webhook processing failed: {str(e)}"
        )


@router.get("/stress", response_model=Dict[str, Any])
async def get_stress_indicators(
    bioauth_service: BioAuthService = Depends(get_bioauth_service),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get stress indicators based on HRV data from wearable devices.

    This endpoint provides an analysis of the user's stress levels based on
    heart rate variability (HRV) data collected from their wearable devices.
    It returns stress indicators that can be used for scheduling decisions.
    """
    try:
        stress_data = await bioauth_service.get_hrv_stress_indicators(
            user_id=str(current_user.id), db=db
        )
        return stress_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to retrieve stress indicators: {str(e)}",
        )


@router.get("/cognitive-load", response_model=Dict[str, Any])
async def get_cognitive_load(
    bioauth_service: BioAuthService = Depends(get_bioauth_service),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get cognitive load estimate based on biometric data.

    This endpoint provides an estimate of the user's current cognitive load
    based on multiple biometric indicators. This can be used to schedule tasks
    of appropriate complexity based on the user's current cognitive capacity.
    """
    try:
        cognitive_data = await bioauth_service.get_cognitive_load_estimate(
            user_id=str(current_user.id), db=db
        )
        return cognitive_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to retrieve cognitive load estimate: {str(e)}",
        )
