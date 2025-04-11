"""
BioAuth-25 Wearable API Service

This module implements the BioAuth-25 standards for wearable device authentication and
biometric data integration. It provides secure connections to wearable devices and
processes physiological data for enhancing scheduling decisions.

Based on the BioAuth-25 specification outlined in the 2025 Wearable Technology Symposium.
"""

import asyncio
import hmac
import hashlib
import json
import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union, Any

import aiohttp
from fastapi import Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.core.config import settings
from app.database import get_db
from app.models.user_model import UserModel
from sqlalchemy.ext.asyncio import AsyncSession
from urllib.parse import urljoin, quote
import requests

logger = logging.getLogger(__name__)


# Define BioAuth-25 data models
class BiometricType(str, Enum):
    """Types of biometric data supported by BioAuth-25."""

    HEART_RATE = "heart_rate"
    HRV = "heart_rate_variability"
    EDA = "electrodermal_activity"  # Skin conductance
    TEMPERATURE = "skin_temperature"
    RESPIRATORY_RATE = "respiratory_rate"
    SLEEP = "sleep_metrics"
    ACTIVITY = "activity_metrics"
    STRESS = "stress_index"
    COGNITIVE_LOAD = "cognitive_load"


class WearableDeviceType(str, Enum):
    """Types of supported wearable devices."""

    SMARTWATCH = "smartwatch"
    FITNESS_TRACKER = "fitness_tracker"
    SMART_RING = "smart_ring"
    SMART_PATCH = "smart_patch"
    SMART_CLOTHING = "smart_clothing"
    EEG_HEADBAND = "eeg_headband"
    MEDICAL_DEVICE = "medical_device"


class BioAuthDeviceInfo(BaseModel):
    """Information about a connected BioAuth-25 device."""

    device_id: str
    device_type: WearableDeviceType
    manufacturer: str
    model: str
    firmware_version: str
    supported_metrics: List[BiometricType]
    connection_status: str
    last_sync: datetime
    battery_level: Optional[float] = None


class BiometricDataPoint(BaseModel):
    """A single biometric data point from a wearable device."""

    metric_type: BiometricType
    timestamp: datetime
    value: float
    confidence: float = Field(ge=0.0, le=1.0)
    device_id: str
    context: Optional[Dict[str, Any]] = None


class BiometricBatch(BaseModel):
    """A batch of biometric data points."""

    user_id: str
    device_id: str
    data_points: List[BiometricDataPoint]
    batch_id: str
    collected_at: datetime


class BioAuthCredential(BaseModel):
    """Secure credential for BioAuth-25 device authentication."""

    device_id: str
    user_id: str
    access_token: str
    refresh_token: str
    expires_at: datetime
    scope: List[str]


class BioAuthService:
    """
    Implements the BioAuth-25 standard for wearable device authentication and
    biometric data integration.
    """

    def __init__(self):
        """Initialize the BioAuth service with configuration settings."""
        self.base_url = settings.BIOAUTH_API_BASE_URL
        self.api_key = settings.BIOAUTH_API_KEY
        self.client_id = settings.BIOAUTH_CLIENT_ID
        self.client_secret = settings.BIOAUTH_CLIENT_SECRET

        # Cache for device connections and credentials
        self._device_cache: Dict[str, BioAuthDeviceInfo] = {}
        self._credential_cache: Dict[str, BioAuthCredential] = {}

        # Queue for processing biometric data
        self._data_queue: asyncio.Queue = asyncio.Queue()

        # Start background processing task
        self._processing_task = None

    async def start_background_processing(self):
        """Start the background task for processing biometric data."""
        if self._processing_task is None:
            self._processing_task = asyncio.create_task(self._process_biometric_data())
            logger.info("Started BioAuth background processing task")

    async def stop_background_processing(self):
        """Stop the background task for processing biometric data."""
        if self._processing_task:
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass
            self._processing_task = None
            logger.info("Stopped BioAuth background processing task")

    async def _process_biometric_data(self):
        """Background task to process incoming biometric data."""
        while True:
            try:
                batch: BiometricBatch = await self._data_queue.get()
                # Process the batch of biometric data
                await self._store_biometric_data(batch)
                await self._analyze_biometric_data(batch)
                self._data_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing biometric data: {str(e)}")

    async def _store_biometric_data(self, batch: BiometricBatch):
        """Store biometric data in the database."""
        # Implementation will depend on database schema
        logger.debug(f"Storing {len(batch.data_points)} biometric data points")
        # TODO: Implement database storage

    async def _analyze_biometric_data(self, batch: BiometricBatch):
        """Analyze biometric data for insights."""
        # Extract patterns and insights from biometric data
        logger.debug(f"Analyzing biometric batch {batch.batch_id}")
        # TODO: Implement analysis logic

    def _build_url(self, path: str) -> str:
        """Safely construct URL by properly encoding path components."""
        if not self.base_url:
            raise HTTPException(status_code=500, detail="BioAuth API base URL not configured")

        # Ensure path is properly encoded
        encoded_path = quote(path.strip("/"))
        return urljoin(self.base_url.rstrip("/") + "/", encoded_path)

    async def verify_biometric(self, user_id: str, biometric_data: Dict) -> bool:
        """Verify user's biometric data."""
        try:
            url = self._build_url(f"verify/{user_id}")
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            response = requests.post(url, json=biometric_data, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json().get("verified", False)

        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail=f"BioAuth verification failed: {str(e)}")

    async def register_biometric(self, user_id: str, biometric_data: Dict) -> bool:
        """Register new biometric data for a user."""
        try:
            url = self._build_url(f"register/{user_id}")
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            response = requests.post(url, json=biometric_data, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json().get("registered", False)

        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail=f"BioAuth registration failed: {str(e)}")

    async def register_device(
        self,
        user_id: str,
        device_type: WearableDeviceType,
        manufacturer: str,
        model: str,
        device_identifier: str,
        auth_code: str,
        db: AsyncSession,
    ) -> BioAuthDeviceInfo:
        """
        Register a new wearable device for a user using the BioAuth-25 protocol.

        Args:
            user_id: The ID of the user registering the device
            device_type: The type of wearable device
            manufacturer: The device manufacturer
            model: The device model
            device_identifier: A unique identifier for the device
            auth_code: Authorization code from the device's authentication flow
            db: Database session

        Returns:
            BioAuthDeviceInfo: Information about the registered device
        """
        # Validate the authorization code with the device manufacturer's API
        async with aiohttp.ClientSession() as session:
            token_url = f"{self.base_url}/auth/token"
            headers = {"Content-Type": "application/json", "X-API-Key": self.api_key}
            payload = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "auth_code": auth_code,
                "device_id": device_identifier,
                "device_type": device_type,
                "user_id": user_id,
            }

            async with session.post(token_url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Device registration failed: {error_text}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Device registration failed: {error_text}",
                    )

                token_data = await response.json()

                # Create and store credentials
                credential = BioAuthCredential(
                    device_id=device_identifier,
                    user_id=user_id,
                    access_token=token_data["access_token"],
                    refresh_token=token_data["refresh_token"],
                    expires_at=datetime.utcnow() + timedelta(seconds=token_data["expires_in"]),
                    scope=token_data["scope"].split(),
                )
                self._credential_cache[device_identifier] = credential

                # TODO: Store credential in database for persistence

        # Get device capabilities
        device_info = await self._get_device_info(device_identifier, credential.access_token)
        self._device_cache[device_identifier] = device_info

        # TODO: Store device info in database

        return device_info

    async def _get_device_info(self, device_id: str, access_token: str) -> BioAuthDeviceInfo:
        """Get device information from the BioAuth API."""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/devices/{device_id}"
            headers = {"Authorization": f"Bearer {access_token}", "X-API-Key": self.api_key}

            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Failed to get device info: {error_text}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Failed to get device info: {error_text}",
                    )

                data = await response.json()

                return BioAuthDeviceInfo(
                    device_id=data["device_id"],
                    device_type=data["device_type"],
                    manufacturer=data["manufacturer"],
                    model=data["model"],
                    firmware_version=data["firmware_version"],
                    supported_metrics=[BiometricType(m) for m in data["supported_metrics"]],
                    connection_status=data["connection_status"],
                    last_sync=datetime.fromisoformat(data["last_sync"]),
                    battery_level=data.get("battery_level"),
                )

    async def get_user_devices(self, user_id: str, db: AsyncSession) -> List[BioAuthDeviceInfo]:
        """Get all registered devices for a user."""
        # TODO: Implement database query to get user devices
        # For now, return from cache if available
        return [
            device
            for device_id, device in self._device_cache.items()
            if device_id in self._credential_cache
            and self._credential_cache[device_id].user_id == user_id
        ]

    async def get_recent_biometric_data(
        self,
        user_id: str,
        device_id: str,
        metric_type: BiometricType,
        start_time: datetime,
        end_time: datetime,
        db: AsyncSession,
    ) -> List[BiometricDataPoint]:
        """
        Get recent biometric data for a specific metric from a device.

        Args:
            user_id: The user ID
            device_id: The device ID
            metric_type: The type of biometric metric to retrieve
            start_time: The start time for the data range
            end_time: The end time for the data range
            db: Database session

        Returns:
            List[BiometricDataPoint]: The retrieved biometric data points
        """
        # Ensure device is registered and credential is valid
        if device_id not in self._credential_cache:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Device {device_id} not registered for user {user_id}",
            )

        credential = self._credential_cache[device_id]
        if credential.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this device's data",
            )

        # Check if token needs refresh
        if credential.expires_at <= datetime.utcnow() + timedelta(minutes=5):
            await self._refresh_token(device_id)

        # Fetch data from device API
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/data/{device_id}/{metric_type}"
            headers = {
                "Authorization": f"Bearer {credential.access_token}",
                "X-API-Key": self.api_key,
            }
            params = {"start_time": start_time.isoformat(), "end_time": end_time.isoformat()}

            async with session.get(url, headers=headers, params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Failed to get biometric data: {error_text}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Failed to get biometric data: {error_text}",
                    )

                data = await response.json()

                return [
                    BiometricDataPoint(
                        metric_type=BiometricType(item["metric_type"]),
                        timestamp=datetime.fromisoformat(item["timestamp"]),
                        value=item["value"],
                        confidence=item.get("confidence", 1.0),
                        device_id=device_id,
                        context=item.get("context"),
                    )
                    for item in data["data_points"]
                ]

    async def _refresh_token(self, device_id: str):
        """Refresh the access token for a device."""
        if device_id not in self._credential_cache:
            logger.error(f"Cannot refresh token for unknown device {device_id}")
            return

        credential = self._credential_cache[device_id]

        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/auth/refresh"
            headers = {"Content-Type": "application/json", "X-API-Key": self.api_key}
            payload = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": credential.refresh_token,
                "device_id": device_id,
                "user_id": credential.user_id,
            }

            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Token refresh failed: {error_text}")
                    # Remove from cache so a new registration is required
                    self._credential_cache.pop(device_id, None)
                    return

                token_data = await response.json()

                # Update credential
                credential.access_token = token_data["access_token"]
                credential.refresh_token = token_data["refresh_token"]
                credential.expires_at = datetime.utcnow() + timedelta(
                    seconds=token_data["expires_in"]
                )

                # TODO: Update database record

    async def process_webhook(self, webhook_data: Dict[str, Any]):
        """
        Process a webhook notification from a wearable device or service.

        This handles real-time updates from devices, including new data availability,
        device status changes, and alerts.
        """
        webhook_type = webhook_data.get("type")

        if webhook_type == "data_update":
            # New data is available
            device_id = webhook_data.get("device_id")
            user_id = webhook_data.get("user_id")

            if device_id and user_id and device_id in self._credential_cache:
                # Verify webhook authenticity using HMAC
                if not self._verify_webhook_signature(webhook_data):
                    logger.warning(f"Invalid webhook signature for device {device_id}")
                    return {"status": "error", "message": "Invalid signature"}

                # Process the data update
                if "data" in webhook_data:
                    batch = BiometricBatch(
                        user_id=user_id,
                        device_id=device_id,
                        data_points=[
                            BiometricDataPoint(
                                metric_type=BiometricType(item["metric_type"]),
                                timestamp=datetime.fromisoformat(item["timestamp"]),
                                value=item["value"],
                                confidence=item.get("confidence", 1.0),
                                device_id=device_id,
                                context=item.get("context"),
                            )
                            for item in webhook_data["data"]
                        ],
                        batch_id=webhook_data.get("batch_id", f"{device_id}_{int(time.time())}"),
                        collected_at=datetime.fromisoformat(
                            webhook_data.get("collected_at", datetime.utcnow().isoformat())
                        ),
                    )

                    # Add to processing queue
                    await self._data_queue.put(batch)

                    return {"status": "success", "message": "Data received"}

        elif webhook_type == "device_status":
            # Device status update
            device_id = webhook_data.get("device_id")

            if device_id in self._device_cache:
                # Update device status
                self._device_cache[device_id].connection_status = webhook_data.get(
                    "status", "unknown"
                )
                self._device_cache[device_id].battery_level = webhook_data.get("battery_level")
                self._device_cache[device_id].last_sync = datetime.fromisoformat(
                    webhook_data.get("last_sync", datetime.utcnow().isoformat())
                )

                # TODO: Update database record

                return {"status": "success", "message": "Status updated"}

        return {"status": "error", "message": "Unknown webhook type or invalid data"}

    def _verify_webhook_signature(self, webhook_data: Dict[str, Any]) -> bool:
        """Verify the HMAC signature of a webhook payload."""
        if "signature" not in webhook_data:
            return False

        received_signature = webhook_data.pop("signature")

        # Create canonical string from sorted keys
        canonical_data = json.dumps(webhook_data, sort_keys=True)

        # Calculate HMAC signature
        calculated_signature = hmac.new(
            self.client_secret.encode(), canonical_data.encode(), hashlib.sha256
        ).hexdigest()

        # Put the signature back
        webhook_data["signature"] = received_signature

        # Compare signatures
        return hmac.compare_digest(calculated_signature, received_signature)

    async def get_hrv_stress_indicators(self, user_id: str, db: AsyncSession) -> Dict[str, Any]:
        """
        Get heart rate variability (HRV) stress indicators for a user.

        This is a higher-level function that analyzes raw HRV data to provide
        stress indicators that can be used for scheduling decisions.
        """
        # Get user's devices
        devices = await self.get_user_devices(user_id, db)

        # Find devices that support HRV
        hrv_devices = [
            device for device in devices if BiometricType.HRV in device.supported_metrics
        ]

        if not hrv_devices:
            return {
                "status": "no_data",
                "message": "No devices with HRV capabilities found for user",
            }

        # Use the most recently synced device
        device = max(hrv_devices, key=lambda d: d.last_sync)

        # Get HRV data for the last 24 hours
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=24)

        try:
            hrv_data = await self.get_recent_biometric_data(
                user_id=user_id,
                device_id=device.device_id,
                metric_type=BiometricType.HRV,
                start_time=start_time,
                end_time=end_time,
                db=db,
            )

            if not hrv_data:
                return {
                    "status": "no_data",
                    "message": "No HRV data available for the specified time period",
                }

            # Analyze HRV data to extract stress indicators
            # This is a simplified analysis for demonstration
            # A real implementation would use more sophisticated algorithms

            # Calculate average HRV over different periods
            all_values = [point.value for point in hrv_data]
            avg_hrv = sum(all_values) / len(all_values) if all_values else 0

            # Current HRV (last hour)
            recent_cutoff = end_time - timedelta(hours=1)
            recent_values = [point.value for point in hrv_data if point.timestamp >= recent_cutoff]
            current_hrv = sum(recent_values) / len(recent_values) if recent_values else 0

            # Calculate stress level (simplified)
            # Lower HRV generally indicates higher stress
            # This is a very simplified model
            baseline_hrv = avg_hrv
            stress_ratio = baseline_hrv / current_hrv if current_hrv > 0 else 1.0

            # Normalize to 0-100 scale (simplified)
            stress_level = min(100, max(0, (stress_ratio - 0.8) * 100))

            return {
                "status": "success",
                "stress_level": stress_level,
                "current_hrv": current_hrv,
                "baseline_hrv": baseline_hrv,
                "readings_count": len(hrv_data),
                "latest_reading_time": max(point.timestamp for point in hrv_data).isoformat(),
                "device": {
                    "id": device.device_id,
                    "model": device.model,
                    "manufacturer": device.manufacturer,
                },
            }

        except Exception as e:
            logger.error(f"Error analyzing HRV data: {str(e)}")
            return {"status": "error", "message": f"Error analyzing HRV data: {str(e)}"}

    async def get_cognitive_load_estimate(self, user_id: str, db: AsyncSession) -> Dict[str, Any]:
        """
        Estimate current cognitive load based on multiple biometric indicators.

        This function combines data from multiple sensors to provide an estimate
        of the user's current cognitive load, which can be used to make scheduling
        decisions that don't overwhelm the user.
        """
        # Get user's devices
        devices = await self.get_user_devices(user_id, db)

        if not devices:
            return {"status": "no_data", "message": "No devices found for user"}

        # Identify which metrics we can collect
        available_metrics = set()
        device_map = {}

        for device in devices:
            for metric in device.supported_metrics:
                available_metrics.add(metric)
                if metric not in device_map:
                    device_map[metric] = []
                device_map[metric].append(device)

        # Define metrics for cognitive load estimation in order of preference
        cognitive_metrics = [
            BiometricType.COGNITIVE_LOAD,  # Direct measurement if available
            BiometricType.HRV,  # Heart rate variability
            BiometricType.HEART_RATE,  # Heart rate
            BiometricType.EDA,  # Electrodermal activity
            BiometricType.STRESS,  # Stress index
            BiometricType.RESPIRATORY_RATE,  # Respiratory rate
        ]

        # Collect data from available metrics
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=1)  # Last hour

        data_points = {}
        for metric in cognitive_metrics:
            if metric in available_metrics and metric in device_map:
                # Use the most recently synced device for this metric
                device = max(device_map[metric], key=lambda d: d.last_sync)

                try:
                    metric_data = await self.get_recent_biometric_data(
                        user_id=user_id,
                        device_id=device.device_id,
                        metric_type=metric,
                        start_time=start_time,
                        end_time=end_time,
                        db=db,
                    )

                    if metric_data:
                        data_points[metric] = metric_data
                except Exception as e:
                    logger.warning(f"Error fetching {metric} data: {str(e)}")

        if not data_points:
            return {
                "status": "no_data",
                "message": "No relevant biometric data available for cognitive load estimation",
            }

        # Process data to estimate cognitive load
        # This is a simplified algorithm for demonstration
        cognitive_load = 50  # Default mid-level
        confidence = 0.0

        # If we have direct cognitive load measurement, use it
        if BiometricType.COGNITIVE_LOAD in data_points:
            points = data_points[BiometricType.COGNITIVE_LOAD]
            values = [point.value for point in points]
            weights = [point.confidence for point in points]
            cognitive_load = (
                sum(v * w for v, w in zip(values, weights)) / sum(weights) if weights else 0
            )
            confidence = 0.9  # High confidence
        else:
            # Combine multiple metrics with a weighted approach
            component_values = {}
            component_weights = {
                BiometricType.HRV: 0.35,
                BiometricType.HEART_RATE: 0.2,
                BiometricType.EDA: 0.25,
                BiometricType.STRESS: 0.4,
                BiometricType.RESPIRATORY_RATE: 0.15,
            }

            # Calculate normalized values for each component
            for metric, points in data_points.items():
                if metric == BiometricType.COGNITIVE_LOAD:
                    continue  # Already handled above

                values = [point.value for point in points]
                if not values:
                    continue

                # Different handling for different metrics
                if metric == BiometricType.HRV:
                    # Lower HRV means higher cognitive load
                    avg = sum(values) / len(values)
                    # Normalize: 0ms HRV -> 100, 100ms HRV -> 0
                    component_values[metric] = max(0, min(100, 100 - avg))

                elif metric == BiometricType.HEART_RATE:
                    # Higher HR often correlates with higher load
                    avg = sum(values) / len(values)
                    # Normalize: 60bpm -> 0, 120bpm -> 100
                    component_values[metric] = max(0, min(100, (avg - 60) * (100 / 60)))

                elif metric == BiometricType.EDA:
                    # Higher EDA means higher arousal/load
                    avg = sum(values) / len(values)
                    # Normalized by device
                    component_values[metric] = max(0, min(100, avg))

                elif metric == BiometricType.STRESS:
                    # Direct stress measurement
                    avg = sum(values) / len(values)
                    component_values[metric] = max(0, min(100, avg))

                elif metric == BiometricType.RESPIRATORY_RATE:
                    # Higher rate can indicate stress/load
                    avg = sum(values) / len(values)
                    # Normalize: 12 -> 0, 20 -> 100
                    component_values[metric] = max(0, min(100, (avg - 12) * (100 / 8)))

            if component_values:
                # Weighted average of components
                total_weight = sum(component_weights[m] for m in component_values.keys())
                if total_weight > 0:
                    cognitive_load = (
                        sum(
                            component_values[m] * component_weights[m]
                            for m in component_values.keys()
                        )
                        / total_weight
                    )

                    # Confidence based on number and quality of metrics
                    confidence = min(0.85, 0.3 + 0.15 * len(component_values))

        return {
            "status": "success",
            "cognitive_load": cognitive_load,
            "confidence": confidence,
            "metrics_used": list(data_points.keys()),
            "recommended_task_complexity": self._get_recommended_complexity(cognitive_load),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _get_recommended_complexity(self, cognitive_load: float) -> str:
        """Get recommended task complexity based on cognitive load."""
        if cognitive_load < 30:
            return "high"  # Low load, can handle complex tasks
        elif cognitive_load < 70:
            return "medium"  # Moderate load, moderate complexity
        else:
            return "low"  # High load, stick to simple tasks


# Dependency injection
async def get_bioauth_service():
    """Dependency for getting the BioAuth service instance."""
    service = BioAuthService()
    await service.start_background_processing()
    try:
        yield service
    finally:
        await service.stop_background_processing()
