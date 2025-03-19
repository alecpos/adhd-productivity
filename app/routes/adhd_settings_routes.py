from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.user_schema import UserSchema
from app.services.auth_service import get_current_user

adhd_settings_router = APIRouter(prefix="/adhd-settings", tags=["ADHD Settings"])


async def get_adhd_settings_service(
    db: AsyncSession = Depends(get_db),
) -> ADHDSettingsServiceSchema:
    return ADHDSettingsServiceSchema(db)


@adhd_settings_router.get("/profile/{user_id}", response_model=ADHDSettingsResponseSchema)
async def get_adhd_settings(
    user_id: UUID,
    current_user: UserSchema = Depends(get_current_user),
    service: ADHDSettingsServiceSchema = Depends(get_adhd_settings_service),
) -> ADHDSettingsResponseSchema:
    """Get ADHD settings for a user."""
    settings = await service.get_settings(user_id)
    if not settings:
        raise HTTPException(status_code=404, detail="ADHD settings not found")


@adhd_settings_router.patch("/profile/{user_id}", response_model=ADHDSettingsResponseSchema)
async def update_adhd_settings(
    user_id: UUID,
    settings: ADHDSettingsUpdateSchema,
    current_user: UserSchema = Depends(get_current_user),
    service: ADHDSettingsServiceSchema = Depends(get_adhd_settings_service),
) -> ADHDSettingsResponseSchema:
    """Update ADHD settings for a user."""
    updated_settings = await service.update_settings(user_id, settings)
    if not updated_settings:
        raise HTTPException(status_code=404, detail="ADHD settings not found")


@adhd_settings_router.get("/metrics/{user_id}", response_model=ADHDMetricsResponseSchema)
async def get_adhd_metrics(
    user_id: UUID,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: UserSchema = Depends(get_current_user),
    service: ADHDSettingsServiceSchema = Depends(get_adhd_settings_service),
) -> ADHDMetricsResponseSchema:
    """Get ADHD-related metrics for a user."""
    return await service.get_metrics(user_id, start_date, end_date)


@adhd_settings_router.post("/distractions/{user_id}", response_model=DistractionLogResponse)
async def log_distraction(
    user_id: UUID,
    distraction: DistractionLogCreate,
    current_user: UserSchema = Depends(get_current_user),
    service: ADHDSettingsServiceSchema = Depends(get_adhd_settings_service),
) -> DistractionLogSchema:
    """Log a distraction event."""
    return await service.log_distraction(user_id, distraction)


@adhd_settings_router.post("/medication/{user_id}", response_model=MedicationLogResponse)
async def log_medication(
    user_id: UUID,
    medication: MedicationLogCreate,
    current_user: UserSchema = Depends(get_current_user),
    service: ADHDSettingsServiceSchema = Depends(get_adhd_settings_service),
) -> MedicationLogSchema:
    """Log medication intake."""
    return await service.log_medication(user_id, medication)


@adhd_settings_router.get(
    "/recommendations/{user_id}", response_model=ADHDRecommendationsResponseSchema
)
async def get_recommendations(
    user_id: UUID,
    current_user: UserSchema = Depends(get_current_user),
    service: ADHDSettingsServiceSchema = Depends(get_adhd_settings_service),
) -> ADHDRecommendationsResponseSchema:
    """Get personalized ADHD recommendations."""
    return await service.get_recommendations(user_id)


@adhd_settings_router.get("/patterns/{user_id}", response_model=ADHDPatternsResponseSchema)
async def get_patterns(
    user_id: UUID,
    current_user: UserSchema = Depends(get_current_user),
    service: ADHDSettingsServiceSchema = Depends(get_adhd_settings_service),
) -> ADHDPatternsResponseSchema:
    """Get ADHD behavior patterns analysis."""
    return await service.get_patterns(user_id)


@adhd_settings_router.post("/daily-plan/{user_id}", response_model=DailyPlanResponse)
async def generate_daily_plan(
    user_id: UUID,
    date: Optional[datetime] = None,
    current_user: UserSchema = Depends(get_current_user),
    service: ADHDSettingsServiceSchema = Depends(get_adhd_settings_service),
) -> DailyPlanSchema:
    """Generate an ADHD-optimized daily plan."""
    return await service.generate_daily_plan(user_id, date)


@adhd_settings_router.post("/calibrate/{user_id}", response_model=ADHDSettingsResponseSchema)
async def calibrate_settings(
    user_id: UUID,
    current_user: UserSchema = Depends(get_current_user),
    service: ADHDSettingsServiceSchema = Depends(get_adhd_settings_service),
) -> ADHDSettingsResponseSchema:
    """Calibrate ADHD settings based on user data."""
    return await service.calibrate_settings(user_id)
