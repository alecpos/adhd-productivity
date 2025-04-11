"""
Temporal pattern recognition schemas.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class TemporalPatternResponse(BaseModel):
    """Response model for temporal pattern analysis."""

    user_id: str = Field(..., description="ID of the user")
    analysis_date: datetime = Field(
        default_factory=datetime.now, description="Timestamp of analysis"
    )
    patterns: Dict[str, float] = Field(..., description="Detected productivity patterns")
    recommendations: List[str] = Field(..., description="Recommendations based on patterns")
    confidence_score: float = Field(..., description="Confidence score of the analysis")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "analysis_date": "2023-01-01T12:00:00Z",
                "patterns": {
                    "morning_productivity": 0.85,
                    "afternoon_slump": 0.65,
                    "evening_recovery": 0.75,
                },
                "recommendations": [
                    "Schedule important tasks in the morning",
                    "Take a break in the afternoon",
                    "Use evening time for planning",
                ],
                "confidence_score": 0.92,
            }
        }
