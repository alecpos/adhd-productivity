# app/routes/__init__.py
"""API route initialization and configuration."""

import logging

from fastapi import APIRouter

# Import route modules
from app.routes.analytics_routes import router as analytics_router
from app.routes.auth_routes import auth_router
from app.routes.body_doubling_routes import router as body_doubling_router
from app.routes.calendar_routes import router as calendar_router
from app.routes.energy_mapping_routes import router as energy_mapping_router
from app.routes.focus_routes import router as focus_router
from app.routes.gamification_routes import router as gamification_router
from app.routes.health_routes import router as health_router
from app.routes.hyperfocus_routes import router as hyperfocus_router
from app.routes.mental_health_routes import router as mental_health_router
from app.routes.mindfulness_routes import router as mindfulness_router
from app.routes.nlp_routes import router as nlp_router
from app.routes.pomodoro_routes import router as pomodoro_router
from app.routes.scheduling_routes import router as scheduling_router
from app.routes.subscriptions_routes import router as subscriptions_router
from app.routes.task_routes import task_router
from app.routes.time_management_routes import router as time_management_router
from app.routes.user_routes import user_router
from app.routes.voice_command_routes import router as voice_command_router

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Create a central api_router to include all other routers
api_router = APIRouter()

# Include routers with their prefixes
api_router.include_router(analytics_router, prefix="/api/analytics", tags=["analytics"])
api_router.include_router(auth_router, prefix="/api/auth", tags=["auth"])
api_router.include_router(body_doubling_router, prefix="/api/v1", tags=["body-doubling"])
api_router.include_router(calendar_router, prefix="/api/calendar", tags=["calendar"])
api_router.include_router(energy_mapping_router, prefix="/api/energy", tags=["energy"])
api_router.include_router(focus_router, prefix="/api/focus", tags=["focus"])
api_router.include_router(gamification_router, prefix="/api/gamification", tags=["gamification"])
api_router.include_router(health_router, prefix="/api/health", tags=["health"])
api_router.include_router(hyperfocus_router, prefix="/api/hyperfocus", tags=["hyperfocus"])
api_router.include_router(mental_health_router, prefix="/api/mental-health", tags=["mental-health"])
api_router.include_router(mindfulness_router, prefix="/api/mindfulness", tags=["mindfulness"])
api_router.include_router(nlp_router, prefix="/api/nlp", tags=["nlp"])
api_router.include_router(pomodoro_router, prefix="/api/pomodoro", tags=["pomodoro"])
api_router.include_router(scheduling_router, prefix="/api/scheduling", tags=["scheduling"])
api_router.include_router(subscriptions_router, prefix="/api/subscriptions", tags=["subscriptions"])
api_router.include_router(task_router, prefix="/api/tasks", tags=["tasks"])
api_router.include_router(time_management_router, prefix="/api/time-management", tags=["time-management"])
api_router.include_router(user_router, prefix="/api/user", tags=["user"])
api_router.include_router(voice_command_router, prefix="/api/voice", tags=["voice"])

# Export the main router
__all__ = ["api_router", "analytics_router", "auth_router", "body_doubling_router", "calendar_router", "energy_mapping_router", "focus_router", "gamification_router", "health_router", "hyperfocus_router", "mental_health_router", "mindfulness_router", "nlp_router", "pomodoro_router", "scheduling_router", "subscriptions_router", "task_router", "time_management_router", "user_router", "voice_command_router"]
