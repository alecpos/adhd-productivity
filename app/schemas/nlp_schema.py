"""Schemas for NLP parsing and analysis."""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from uuid import UUID

from pydantic import Field, validator

from app.schemas.base_schema import BaseSchema


class NLPParserRequestSchema(BaseSchema):
    """Schema for NLP parsing requests."""
    
    text: str = Field(..., description="Text to be parsed and analyzed")
    context: Optional[str] = Field(None, description="Additional context for parsing")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Parsing options")
    user_preferences: Optional[Dict[str, Any]] = Field(default_factory=dict, description="User-specific parsing preferences")


class NLPParserResponseSchema(BaseSchema):
    """Schema for NLP parsing responses."""
    
    id: UUID
    user_id: UUID
    text: str = Field(..., description="Original text that was parsed")
    parsed_data: Dict[str, Any] = Field(..., description="Structured data extracted from text")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence score of the parsing")
    entities: List[Dict[str, Any]] = Field(default_factory=list, description="Named entities found in text")
    intent: Optional[str] = Field(None, description="Detected intent of the text")
    created_at: datetime
    updated_at: datetime


class NLPAnalysisSchema(BaseSchema):
    """Schema for detailed NLP analysis."""
    
    id: UUID
    text_id: UUID = Field(..., description="ID of the parsed text")
    sentiment_score: float = Field(..., ge=-1, le=1, description="Sentiment analysis score")
    complexity_score: float = Field(..., ge=0, le=1, description="Text complexity score")
    key_phrases: List[str] = Field(..., description="Extracted key phrases")
    topics: List[Dict[str, float]] = Field(..., description="Topic analysis with confidence scores")
    summary: Optional[str] = Field(None, description="Generated summary of the text")
    recommendations: List[str] = Field(default_factory=list, description="AI-generated recommendations")
    meta_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional analysis metadata")
    created_at: datetime


class NLPTaskParseSchema(BaseSchema):
    """Schema for parsing text into task data."""
    
    title: str = Field(..., description="Extracted task title")
    description: Optional[str] = Field(None, description="Extracted task description")
    due_date: Optional[datetime] = Field(None, description="Extracted due date")
    priority: Optional[int] = Field(None, ge=1, le=5, description="Extracted priority level")
    tags: List[str] = Field(default_factory=list, description="Extracted tags or categories")
    subtasks: List[Dict[str, Any]] = Field(default_factory=list, description="Extracted subtasks")
    recurring: Optional[Dict[str, Any]] = Field(None, description="Recurring schedule information")
    meta_data: Dict[str, Any] = Field(default_factory=dict, description="Additional parsed metadata")


class TaskComplexityAnalysisSchema(BaseSchema):
    """Schema for ADHD-specific task complexity analysis."""
    
    task_id: UUID
    complexity_level: int = Field(..., ge=1, le=5, description="Overall task complexity rating")
    time_estimate: int = Field(..., description="Estimated time in minutes")
    focus_requirements: Dict[str, float] = Field(..., description="Different types of focus required")
    potential_challenges: List[str] = Field(..., description="ADHD-specific challenges")
    breakdown_suggestions: List[Dict[str, Any]] = Field(..., description="Suggestions for breaking down task")
    energy_level_recommendation: str = Field(..., description="Best energy level to tackle this task")
    adhd_friendly_score: float = Field(..., ge=0, le=1, description="How ADHD-friendly the task is")


class FocusStrategySchema(BaseSchema):
    """Schema for personalized focus strategies."""
    
    strategy_id: UUID
    task_type: str = Field(..., description="Type of task this strategy is for")
    title: str = Field(..., description="Name of the strategy")
    description: str = Field(..., description="Detailed explanation of the strategy")
    duration: int = Field(..., description="Recommended duration in minutes")
    break_intervals: List[int] = Field(..., description="Suggested break intervals")
    environment_setup: List[str] = Field(..., description="Environmental recommendations")
    tools_needed: List[str] = Field(default_factory=list, description="Tools or resources needed")
    effectiveness_rating: Optional[float] = Field(None, ge=0, le=1, description="User-specific effectiveness rating")
    user_notes: Optional[str] = Field(None, description="User's notes about this strategy")


class NLPProcessingOptionsSchema(BaseSchema):
    """Schema for configuring NLP processing options."""
    
    language: str = Field(default="en", description="Language code for processing")
    max_tokens: int = Field(default=512, description="Maximum tokens to process")
    model_preferences: Dict[str, Any] = Field(default_factory=dict, description="Model-specific settings")
    analysis_depth: str = Field(default="standard", description="Depth of analysis: quick, standard, or deep")
    custom_entities: Optional[List[Dict[str, Any]]] = Field(None, description="Custom entity definitions")
    confidence_threshold: float = Field(default=0.7, ge=0, le=1, description="Minimum confidence score threshold")

    @validator("analysis_depth")
    def validate_analysis_depth(cls, v):
        allowed_values = ["quick", "standard", "deep"]
        if v not in allowed_values:
            raise ValueError(f"analysis_depth must be one of {allowed_values}")
        return v


__all__ = [
    "NLPParserRequestSchema",
    "NLPParserResponseSchema",
    "NLPAnalysisSchema",
    "NLPTaskParseSchema",
    "TaskComplexityAnalysisSchema",
    "FocusStrategySchema",
    "NLPProcessingOptionsSchema"
] 