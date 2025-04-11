"""ADHD settings schemas."""

from app.schemas.base_schema import BaseSchema
from pydantic import Field, BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID


class DistractionSensitivitySchema(BaseSchema):
    """Distraction sensitivity settings."""

    visual: float = Field(5.0, ge=0, le=10, description="Visual distraction sensitivity (0-10)")
    auditory: float = Field(5.0, ge=0, le=10, description="Auditory distraction sensitivity (0-10)")
    movement: float = Field(5.0, ge=0, le=10, description="Movement distraction sensitivity (0-10)")
    internal: float = Field(5.0, ge=0, le=10, description="Internal distraction sensitivity (0-10)")


class TimeBlockSchema(BaseSchema):
    """Time block for energy management."""

    start: str = Field(..., description="Start time in HH:MM format")
    end: str = Field(..., description="End time in HH:MM format")


class EnergyManagementSchema(BaseSchema):
    """Energy management settings."""

    peakHours: List[TimeBlockSchema] = Field(default_factory=list, description="Peak energy hours")
    lowEnergyPeriods: List[TimeBlockSchema] = Field(
        default_factory=list, description="Low energy periods"
    )
    energyRecoveryRate: int = Field(
        30, ge=5, le=120, description="Minutes needed to recover after intense focus"
    )
    sustainedFocusLimit: int = Field(
        45, ge=10, le=180, description="Minutes before needing a break"
    )


class ExecutiveFunctionSettingsSchema(BaseSchema):
    """Executive function support settings."""

    taskInitiationSupport: bool = Field(True, description="Enable task initiation support")
    taskSwitchingAssistance: bool = Field(True, description="Enable task switching assistance")
    timeBlindnessCompensation: bool = Field(True, description="Enable time blindness compensation")
    workingMemoryAids: bool = Field(True, description="Enable working memory aids")
    prioritizationHelp: bool = Field(True, description="Enable prioritization help")


class MedicationScheduleSchema(BaseSchema):
    """Medication schedule settings."""

    times: List[str] = Field(default_factory=list, description="Medication times in HH:MM format")
    duration: int = Field(8, ge=1, le=24, description="Effect duration in hours")
    peakTime: int = Field(2, ge=0, le=12, description="Hours after taking when most effective")


class AccommodationsSchema(BaseSchema):
    """ADHD accommodations settings."""

    needsExternalAccountability: bool = Field(True, description="Needs external accountability")
    prefersVisualInformation: bool = Field(True, description="Prefers visual information")
    requiresFrequentBreaks: bool = Field(True, description="Requires frequent breaks")
    needsDeadlineBuffer: bool = Field(True, description="Needs deadline buffer")
    strugglesWith: List[str] = Field(default_factory=list, description="Areas of struggle")
    copingStrategies: List[str] = Field(default_factory=list, description="Coping strategies")


class ADHDSettingsBaseSchema(BaseSchema):
    """Base ADHD settings schema."""

    distraction_sensitivity: DistractionSensitivitySchema
    energy_management: EnergyManagementSchema
    executive_function: ExecutiveFunctionSettingsSchema
    medication_schedule: Optional[MedicationScheduleSchema] = None
    accommodations: AccommodationsSchema


class ADHDSettingsCreateSchema(ADHDSettingsBaseSchema):
    """ADHD settings creation schema."""


class ADHDSettingsUpdateSchema(ADHDSettingsBaseSchema):
    """ADHD settings update schema."""

    distraction_sensitivity: Optional[DistractionSensitivitySchema] = None
    energy_management: Optional[EnergyManagementSchema] = None
    executive_function: Optional[ExecutiveFunctionSettingsSchema] = None
    medication_schedule: Optional[MedicationScheduleSchema] = None
    accommodations: Optional[AccommodationsSchema] = None


class ADHDSettingsResponseSchema(ADHDSettingsBaseSchema):
    """ADHD settings response schema."""

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DistractionLogCreateSchema(BaseSchema):
    """Distraction log creation schema."""

    type: str = Field(..., description="Type of distraction")
    duration: int = Field(..., ge=0, description="Duration in minutes")
    impact: int = Field(..., ge=1, le=10, description="Impact level (1-10)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DistractionLogResponseSchema(DistractionLogCreateSchema):
    """Distraction log response schema."""

    id: UUID
    user_id: UUID

    model_config = {"from_attributes": True}


class MedicationLogCreateSchema(BaseSchema):
    """Medication log creation schema."""

    effectiveness: float = Field(..., ge=0, le=1, description="Effectiveness score (0-1)")
    side_effects: Optional[List[str]] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MedicationLogResponseSchema(MedicationLogCreateSchema):
    """Medication log response schema."""

    id: UUID
    user_id: UUID

    model_config = {"from_attributes": True}


class ADHDMetricsResponseSchema(BaseSchema):
    """ADHD metrics response schema."""

    focus_scores: Dict[str, Any] = Field(..., description="Focus scores by timeframe")
    task_completion: Dict[str, float] = Field(
        ..., description="TaskModelSchema completion statistics"
    )
    medication_effectiveness: float = Field(..., ge=0, le=1)
    productive_hours: List[str] = Field(..., description="Productive hours")
    distraction_patterns: List[Dict[str, Any]] = Field(
        ..., description="Distraction patterns analysis"
    )


class ADHDRecommendationsResponseSchema(BaseSchema):
    """ADHD recommendations response schema."""

    scheduling: List[str] = Field(..., description="Scheduling recommendations")
    environment: List[str] = Field(..., description="Environment recommendations")
    strategies: List[str] = Field(..., description="Strategy recommendations")
    accommodations: List[str] = Field(..., description="Accommodation recommendations")


class ADHDPatternsResponseSchema(BaseSchema):
    """ADHD patterns response schema."""

    productivity: List[Dict[str, str]] = Field(..., description="Productivity patterns")
    distractions: List[Dict[str, str]] = Field(..., description="Distraction patterns")
    success_factors: List[str] = Field(..., description="Success factors")


class ADHDDailyPlanResponseSchema(BaseSchema):
    """Daily plan response schema."""

    medication_timing: List[str] = Field(..., description="Medication timing recommendations")
    break_schedule: List[str] = Field(..., description="Break schedule")
    focus_blocks: List[Dict[str, str]] = Field(..., description="Focus block schedule")
    accommodations: List[str] = Field(..., description="Daily accommodations")
