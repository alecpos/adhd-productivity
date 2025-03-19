"""API endpoints for Temporal Pattern Recognition."""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.database import get_db
from app.ml.temporal_pattern_recognition import TemporalPatternRecognitionService
from app.schemas.time_block_schema import TimeBlockCreate, TimeBlockResponse
from app.schemas.user_schema import UserResponseSchema
from app.schemas.mental_health_schema import MentalHealthLogResponseSchema
from app.schemas.productivity_schema import ProductivityResponseSchema
from app.schemas.energy_schema import EnergyLogResponseSchema
from app.api.deps import get_current_user

router = APIRouter(prefix="/tpr", tags=["Temporal Pattern Recognition"])


@router.post("/analyze_productivity_patterns")
async def analyze_productivity_patterns(
    user_id: str,
    days: int = Query(30, description="Number of days of historical data to analyze"),
    days_to_predict: int = Query(7, description="Number of days to predict patterns for"),
    current_user: UserResponseSchema = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Analyze productivity patterns using LSTM models.
    
    This endpoint implements functionality from STORY-1: LSTM infrastructure for 
    productivity pattern detection.
    """
    # Ensure user has permission to access this data
    if user_id != str(current_user.id) and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this user's data")
    
    # Get time blocks for specified user and time period
    from app.crud.time_block_crud import time_block_crud
    from app.crud.mental_health_crud import mental_health_crud
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    time_blocks = await time_block_crud.get_multi_by_user_and_date_range(
        db, user_id=user_id, start_date=start_date, end_date=end_date
    )
    mental_health_logs = await mental_health_crud.get_multi_by_user_and_date_range(
        db, user_id=user_id, start_date=start_date, end_date=end_date
    )
    
    # Convert models to dictionaries
    time_block_dicts = [tb.to_dict() for tb in time_blocks]
    mental_health_dicts = [mh.to_dict() for mh in mental_health_logs]
    
    # Create service and analyze patterns
    tpr_service = TemporalPatternRecognitionService(db)
    results = await tpr_service.analyze_productivity_patterns(
        user_id, time_block_dicts, mental_health_dicts, days_to_predict
    )
    
    return {
        "user_id": user_id,
        "analysis_date": datetime.now().isoformat(),
        "data_range": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "results": results
    }


@router.post("/model_circadian_rhythm")
async def model_circadian_rhythm(
    user_id: str,
    days: int = Query(30, description="Number of days of historical data to analyze"),
    current_user: UserResponseSchema = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Model user's circadian rhythm for optimal task allocation.
    
    This endpoint implements functionality from STORY-2: Circadian rhythm modeling for 
    optimal task allocation.
    """
    # Ensure user has permission to access this data
    if user_id != str(current_user.id) and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this user's data")
    
    # Get energy logs and user data
    from app.crud.energy_crud import energy_crud
    from app.crud.user_crud import user_crud
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    energy_logs = await energy_crud.get_multi_by_user_and_date_range(
        db, user_id=user_id, start_date=start_date, end_date=end_date
    )
    user = await user_crud.get(db, id=user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Convert models to dictionaries
    energy_log_dicts = [el.to_dict() for el in energy_logs]
    user_data = user.to_dict()
    
    # Add sleep data from user preferences if available
    if hasattr(user, "preferences") and user.preferences:
        if "sleep_time" in user.preferences:
            user_data["sleep_time"] = user.preferences["sleep_time"]
        if "wake_time" in user.preferences:
            user_data["wake_time"] = user.preferences["wake_time"]
    
    # Create service and model circadian rhythm
    tpr_service = TemporalPatternRecognitionService(db)
    results = await tpr_service.model_circadian_rhythm(
        user_id, energy_log_dicts, user_data
    )
    
    return {
        "user_id": user_id,
        "analysis_date": datetime.now().isoformat(),
        "data_range": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "results": results
    }


@router.post("/generate_productivity_insights")
async def generate_productivity_insights(
    user_id: str,
    days: int = Query(30, description="Number of days of historical data to analyze"),
    current_user: UserResponseSchema = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate productivity insights using the correlation system.
    
    This endpoint implements functionality from STORY-3: Multi-feature correlation system for 
    productivity insights.
    """
    # Ensure user has permission to access this data
    if user_id != str(current_user.id) and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this user's data")
    
    # Get required data
    from app.crud.time_block_crud import time_block_crud
    from app.crud.mental_health_crud import mental_health_crud
    from app.crud.productivity_crud import productivity_crud
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    time_blocks = await time_block_crud.get_multi_by_user_and_date_range(
        db, user_id=user_id, start_date=start_date, end_date=end_date
    )
    mental_health_logs = await mental_health_crud.get_multi_by_user_and_date_range(
        db, user_id=user_id, start_date=start_date, end_date=end_date
    )
    productivity_metrics = await productivity_crud.get_multi_by_user_and_date_range(
        db, user_id=user_id, start_date=start_date, end_date=end_date
    )
    
    # Convert models to dictionaries
    time_block_dicts = [tb.to_dict() for tb in time_blocks]
    mental_health_dicts = [mh.to_dict() for mh in mental_health_logs]
    productivity_dicts = [pm.to_dict() for pm in productivity_metrics]
    
    # Create service and generate insights
    tpr_service = TemporalPatternRecognitionService(db)
    results = await tpr_service.generate_productivity_insights(
        user_id, time_block_dicts, mental_health_dicts, productivity_dicts
    )
    
    return {
        "user_id": user_id,
        "analysis_date": datetime.now().isoformat(),
        "data_range": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "results": results
    }


@router.post("/run_federated_analysis")
async def run_federated_analysis(
    user_id: str,
    anonymize: bool = Query(True, description="Whether to anonymize client ID"),
    include_sensitive: bool = Query(False, description="Whether to include sensitive data"),
    current_user: UserResponseSchema = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Run federated analysis for privacy-preserving insights.
    
    This endpoint implements functionality from STORY-4: Federated learning infrastructure for 
    privacy-preserving insights.
    """
    # Ensure user has permission to access this data
    if user_id != str(current_user.id) and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this user's data")
    
    # Get mental health data
    from app.crud.mental_health_crud import mental_health_crud
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)  # Last 30 days
    
    mental_health_logs = await mental_health_crud.get_multi_by_user_and_date_range(
        db, user_id=user_id, start_date=start_date, end_date=end_date
    )
    
    # Prepare mental health data
    mh_data = {
        "mood_scores": [log.mood_score for log in mental_health_logs if log.mood_score is not None],
        "stress_levels": [log.stress_level for log in mental_health_logs if log.stress_level is not None],
        "anxiety_levels": [log.anxiety_level for log in mental_health_logs if log.anxiety_level is not None],
        "sleep_quality": [log.sleep_quality for log in mental_health_logs if log.sleep_quality is not None],
        "sleep_hours": [log.sleep_hours for log in mental_health_logs if log.sleep_hours is not None],
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id
    }
    
    # Create service and run federated analysis
    tpr_service = TemporalPatternRecognitionService(db)
    results = await tpr_service.run_federated_analysis(
        user_id, mh_data, anonymize, include_sensitive
    )
    
    return {
        "user_id": user_id if not anonymize else f"anonymized_user_{uuid.uuid4().hex[:8]}",
        "analysis_date": datetime.now().isoformat(),
        "data_range": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "privacy_settings": {
            "anonymized": anonymize,
            "sensitive_included": include_sensitive
        },
        "results": results
    }


@router.post("/generate_comprehensive_insights")
async def generate_comprehensive_insights(
    user_id: str,
    days: int = Query(30, description="Number of days of historical data to analyze"),
    current_user: UserResponseSchema = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate comprehensive insights using all EPIC-1 models.
    
    This endpoint integrates all four stories from EPIC-1:
    - LSTM infrastructure for productivity pattern detection
    - Circadian rhythm modeling for optimal task allocation
    - Multi-feature correlation system for productivity insights
    - Federated learning infrastructure for privacy-preserving insights
    """
    # Ensure user has permission to access this data
    if user_id != str(current_user.id) and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this user's data")
    
    # Get all required data
    from app.crud.time_block_crud import time_block_crud
    from app.crud.mental_health_crud import mental_health_crud
    from app.crud.productivity_crud import productivity_crud
    from app.crud.energy_crud import energy_crud
    from app.crud.user_crud import user_crud
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    time_blocks = await time_block_crud.get_multi_by_user_and_date_range(
        db, user_id=user_id, start_date=start_date, end_date=end_date
    )
    mental_health_logs = await mental_health_crud.get_multi_by_user_and_date_range(
        db, user_id=user_id, start_date=start_date, end_date=end_date
    )
    productivity_metrics = await productivity_crud.get_multi_by_user_and_date_range(
        db, user_id=user_id, start_date=start_date, end_date=end_date
    )
    energy_logs = await energy_crud.get_multi_by_user_and_date_range(
        db, user_id=user_id, start_date=start_date, end_date=end_date
    )
    user = await user_crud.get(db, id=user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Convert models to dictionaries
    time_block_dicts = [tb.to_dict() for tb in time_blocks]
    mental_health_dicts = [mh.to_dict() for mh in mental_health_logs]
    productivity_dicts = [pm.to_dict() for pm in productivity_metrics]
    energy_log_dicts = [el.to_dict() for el in energy_logs]
    user_data = user.to_dict()
    
    # Create service and generate comprehensive insights
    tpr_service = TemporalPatternRecognitionService(db)
    results = await tpr_service.generate_comprehensive_insights(
        user_id, time_block_dicts, mental_health_dicts, energy_log_dicts, productivity_dicts, user_data
    )
    
    return {
        "user_id": user_id,
        "analysis_date": datetime.now().isoformat(),
        "data_range": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "results": results
    }


@router.post("/optimize_schedule")
async def optimize_schedule(
    user_id: str,
    tasks: List[Dict[str, Any]],
    current_user: UserResponseSchema = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Optimize schedule based on circadian rhythm and energy levels.
    
    This endpoint combines STORY-1 and STORY-2 to create an optimized schedule
    based on productivity patterns and circadian rhythm analysis.
    """
    # Ensure user has permission to access this data
    if user_id != str(current_user.id) and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this user's data")
    
    # Get user data
    from app.crud.user_crud import user_crud
    from app.crud.energy_crud import energy_crud
    
    user = await user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get recent energy logs for circadian rhythm modeling
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    energy_logs = await energy_crud.get_multi_by_user_and_date_range(
        db, user_id=user_id, start_date=start_date, end_date=end_date
    )
    
    # Convert models to dictionaries
    energy_log_dicts = [el.to_dict() for el in energy_logs]
    user_data = user.to_dict()
    
    # Create service
    tpr_service = TemporalPatternRecognitionService(db)
    
    # First, model circadian rhythm
    rhythm_results = await tpr_service.model_circadian_rhythm(
        user_id, energy_log_dicts, user_data
    )
    
    # Create energy pattern from rhythm results
    from app.schemas.scheduling_schema import EnergySchedulingPattern, WorkHours
    energy_pattern = EnergySchedulingPattern(
        hourly_energy_levels={
            int(time.split(":")[0]): level 
            for time, level in rhythm_results["energy_curve"]["hourly_predictions"]
        }
    )
    
    # Get work hours from user preferences
    work_hours = WorkHours(
        start_hour=user_data.get("work_start_hour", 9),
        end_hour=user_data.get("work_end_hour", 17)
    )
    
    # Optimize schedule
    optimized_schedule = await tpr_service.optimize_schedule_with_energy(
        user_id, tasks, energy_pattern, user_data, work_hours
    )
    
    return {
        "user_id": user_id,
        "optimization_date": datetime.now().isoformat(),
        "energy_pattern": {
            "hourly_energy_levels": energy_pattern.hourly_energy_levels
        },
        "work_hours": {
            "start_hour": work_hours.start_hour,
            "end_hour": work_hours.end_hour
        },
        "optimized_schedule": optimized_schedule
    } 