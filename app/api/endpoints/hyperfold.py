"""
Hyperfold Attention API endpoints

This module provides API endpoints for advanced temporal pattern recognition
using the MIT Hyperfold Temporal Attention system.
"""

from typing import Dict, List, Optional, Any, Union
import torch
import numpy as np
from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.database import get_db
from app.ml.hyperfold_attention_v2 import HyperfoldAttentionV2
from app.core.config import settings
from app.core.security.security import get_current_user
from app.models.user_model import UserModel
from app.services.bioauth_service import (
    BioAuthService, 
    get_bioauth_service, 
    BiometricType
)

router = APIRouter(
    prefix="/hyperfold",
    tags=["hyperfold"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Not authenticated"},
        status.HTTP_403_FORBIDDEN: {"description": "Not authorized to access this resource"},
        status.HTTP_404_NOT_FOUND: {"description": "Resource not found"},
    },
)

# Keep a singleton instance of the model for inference
_hyperfold_model = None


def get_hyperfold_model() -> HyperfoldAttentionV2:
    """
    Get the Hyperfold model singleton instance.
    
    This initializes the model if it doesn't exist yet.
    """
    global _hyperfold_model
    
    if _hyperfold_model is None:
        # Define modalities - dimensions are examples and should be adjusted 
        # based on actual data formats
        modalities = {
            "calendar": 64,   # Calendar event features
            "biometric": 32,  # Biometric data features
            "task": 48,       # Task features
            "context": 24     # Environmental/contextual features
        }
        
        # Create the model with multi-modal support
        _hyperfold_model = HyperfoldAttentionV2(
            input_dim=64,     # Fallback for single-modal operation
            hidden_dim=128,
            output_dim=64,
            modalities=modalities,
            manifold_type="hyperbolic",  # Can be "hyperbolic", "spherical", "euclidean", or "product"
            max_window_size=128,
            dropout=0.1
        )
        
        # Load pre-trained weights if available
        try:
            state_dict = torch.load(settings.HYPERFOLD_MODEL_PATH)
            _hyperfold_model.load_state_dict(state_dict)
            _hyperfold_model.eval()  # Set to evaluation mode
        except (FileNotFoundError, RuntimeError) as e:
            # Log that we're using an untrained model
            print(f"Warning: Could not load Hyperfold model weights: {e}")
            print("Using untrained model - results will not be optimal")
    
    return _hyperfold_model


class TemporalPatternRequest(BaseModel):
    """Request for temporal pattern recognition."""
    calendar_data: Optional[List[Dict[str, Any]]] = Field(
        None, 
        description="Calendar event data for pattern recognition"
    )
    task_data: Optional[List[Dict[str, Any]]] = Field(
        None, 
        description="Task data for pattern recognition"
    )
    context_data: Optional[Dict[str, Any]] = Field(
        None, 
        description="Contextual/environmental data"
    )
    time_range: Optional[List[str]] = Field(
        None, 
        description="Time range for analysis in ISO format [start, end]"
    )
    include_biometrics: bool = Field(
        False,
        description="Whether to include biometric data in the analysis"
    )


class TemporalPatternResponse(BaseModel):
    """Response for temporal pattern recognition."""
    optimal_times: List[Dict[str, Any]] = Field(
        ...,
        description="Optimal time slots identified for high productivity"
    )
    pattern_insights: Dict[str, Any] = Field(
        ...,
        description="Insights extracted from temporal patterns"
    )
    focus_predictions: Optional[List[Dict[str, float]]] = Field(
        None,
        description="Predicted focus levels across time periods"
    )
    energy_predictions: Optional[List[Dict[str, float]]] = Field(
        None,
        description="Predicted energy levels across time periods"
    )
    recommended_schedule: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Recommended task scheduling based on patterns"
    )
    metadata: Dict[str, Any] = Field(
        ...,
        description="Additional metadata about the prediction"
    )


@router.post("/patterns", response_model=TemporalPatternResponse)
async def analyze_temporal_patterns(
    request: TemporalPatternRequest,
    bioauth_service: Optional[BioAuthService] = Depends(get_bioauth_service),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze temporal patterns using the enhanced MIT Hyperfold system.
    
    This endpoint processes calendar data, task information, biometric signals,
    and contextual information to identify optimal time periods for different
    types of tasks, predict energy and focus levels, and provide scheduling
    recommendations.
    """
    try:
        # Get the model
        model = get_hyperfold_model()
        
        # Prepare input data for each modality
        modality_data = {}
        
        # Process calendar data if provided
        if request.calendar_data:
            # Preprocess calendar data into tensor format
            # This is a placeholder for actual preprocessing logic
            calendar_tensor = torch.randn(1, len(request.calendar_data), 64)
            modality_data["calendar"] = calendar_tensor
        
        # Process task data if provided
        if request.task_data:
            # Preprocess task data into tensor format
            task_tensor = torch.randn(1, len(request.task_data), 48)
            modality_data["task"] = task_tensor
        
        # Process context data if provided
        if request.context_data:
            # Preprocess context data into tensor format
            context_tensor = torch.randn(1, 10, 24)  # Example: 10 context features
            modality_data["context"] = context_tensor
        
        # Include biometric data if requested
        if request.include_biometrics and bioauth_service:
            # Get biometric data from BioAuth service
            try:
                # Get user devices
                devices = await bioauth_service.get_user_devices(
                    user_id=str(current_user.id),
                    db=db
                )
                
                if devices:
                    # For each device that supports heart rate or HRV, get recent data
                    biometric_data_points = []
                    
                    for device in devices:
                        # Check if device supports heart rate or HRV
                        supported_metrics = [
                            metric for metric in [BiometricType.HEART_RATE, BiometricType.HRV]
                            if metric in device.supported_metrics
                        ]
                        
                        if supported_metrics:
                            # Use first supported metric
                            metric = supported_metrics[0]
                            
                            # Get data for the last 24 hours (or specified time range)
                            if request.time_range and len(request.time_range) == 2:
                                from datetime import datetime
                                start_time = datetime.fromisoformat(request.time_range[0])
                                end_time = datetime.fromisoformat(request.time_range[1])
                            else:
                                from datetime import datetime, timedelta
                                end_time = datetime.utcnow()
                                start_time = end_time - timedelta(hours=24)
                            
                            data = await bioauth_service.get_recent_biometric_data(
                                user_id=str(current_user.id),
                                device_id=device.device_id,
                                metric_type=metric,
                                start_time=start_time,
                                end_time=end_time,
                                db=db
                            )
                            
                            biometric_data_points.extend(data)
                    
                    if biometric_data_points:
                        # Convert biometric data to tensor format
                        # This is a placeholder for actual preprocessing logic
                        biometric_tensor = torch.randn(1, len(biometric_data_points), 32)
                        modality_data["biometric"] = biometric_tensor
            
            except Exception as e:
                # Log error but continue without biometric data
                print(f"Error fetching biometric data: {str(e)}")
        
        # If no data provided, return error
        if not modality_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid data provided for analysis"
            )
        
        # Use placeholder for state features (could be derived from biometrics)
        state_features = torch.randn(1, 16)  # Example: 16 state features
        
        # Run the model inference
        with torch.no_grad():
            output, metadata = model(modality_data, state_features=state_features)
        
        # Process model output to generate response
        # This is a placeholder for actual output processing logic
        
        # Example optimal times (would be derived from actual model output)
        optimal_times = [
            {
                "start_time": "09:00:00",
                "end_time": "11:00:00",
                "task_type": "deep_work",
                "effectiveness": 0.85
            },
            {
                "start_time": "14:30:00",
                "end_time": "16:00:00",
                "task_type": "creative",
                "effectiveness": 0.78
            }
        ]
        
        # Example pattern insights
        pattern_insights = {
            "daily_energy_peak": "10:00:00",
            "daily_energy_trough": "15:00:00",
            "weekly_patterns": {
                "most_productive_day": "Tuesday",
                "least_productive_day": "Friday"
            },
            "task_completion_insights": {
                "best_time_for_deep_work": "Morning",
                "best_time_for_admin_tasks": "Afternoon"
            }
        }
        
        # Example focus predictions (hourly for a day)
        focus_predictions = [
            {"time": f"{hour:02d}:00:00", "focus_level": round(float(np.random.normal(0.7, 0.15)), 2)}
            for hour in range(8, 18)
        ]
        
        # Example energy predictions (hourly for a day)
        energy_predictions = [
            {"time": f"{hour:02d}:00:00", "energy_level": round(float(np.random.normal(0.65, 0.2)), 2)}
            for hour in range(8, 18)
        ]
        
        # Example recommended schedule
        recommended_schedule = [
            {
                "task_id": "task_001",
                "task_name": "Project planning",
                "start_time": "09:00:00",
                "end_time": "10:30:00",
                "confidence": 0.82
            },
            {
                "task_id": "task_002",
                "task_name": "Email processing",
                "start_time": "11:00:00",
                "end_time": "12:00:00",
                "confidence": 0.75
            }
        ]
        
        # Prepare response
        response = TemporalPatternResponse(
            optimal_times=optimal_times,
            pattern_insights=pattern_insights,
            focus_predictions=focus_predictions,
            energy_predictions=energy_predictions,
            recommended_schedule=recommended_schedule,
            metadata={
                "modalities_used": list(modality_data.keys()),
                "biometrics_included": "biometric" in modality_data,
                "model_version": "MIT Hyperfold v2.0",
                "attention_metadata": {
                    "window_sizes": metadata.get("window", {}).get("window_sizes", []).tolist() 
                    if "window" in metadata else []
                }
            }
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing temporal patterns: {str(e)}"
        )


class ManifoldTypeRequest(BaseModel):
    """Request to change the Riemannian manifold type."""
    manifold_type: str = Field(
        ...,
        description="Type of Riemannian manifold to use (hyperbolic, spherical, euclidean, product)"
    )


@router.post("/config/manifold", response_model=Dict[str, Any])
async def update_manifold_type(
    request: ManifoldTypeRequest,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Update the Riemannian manifold type used by the Hyperfold system.
    
    Different manifold types are better suited for different types of temporal data:
    - Hyperbolic: Best for hierarchical patterns and power-law distributions
    - Spherical: Best for cyclical patterns with similar scales
    - Euclidean: Simple linear patterns
    - Product: Combined hyperbolic and spherical for complex data
    
    This endpoint is primarily for experimentation and optimization.
    """
    # Validate manifold type
    valid_types = ["hyperbolic", "spherical", "euclidean", "product"]
    if request.manifold_type.lower() not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid manifold type. Must be one of: {', '.join(valid_types)}"
        )
    
    try:
        # Get the model
        model = get_hyperfold_model()
        
        # Update the manifold type
        # Note: In a real implementation, this would require recreating the model
        # with the new manifold type and possibly re-loading weights
        
        # For this demo, we just return success
        return {
            "status": "success",
            "message": f"Manifold type updated to {request.manifold_type}",
            "manifold_type": request.manifold_type,
            "note": "This is a placeholder. In production, this would require model reconstruction."
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating manifold type: {str(e)}"
        ) 