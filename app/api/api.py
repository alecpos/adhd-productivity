"""Main API router that includes all endpoint routers."""

from fastapi import APIRouter

from app.api.endpoints.temporal_pattern_recognition import router as tpr_router
from app.api.endpoints.commitment_detection import router as commitment_router
from app.api.endpoints.hyperfold import router as hyperfold_router
from app.api.endpoints.bioauth import router as bioauth_router
from app.api.endpoints.accessibility import router as accessibility_router
from app.api.endpoints.project_management import router as project_management_router
from app.api.endpoints.calendar_integration import router as calendar_integration_router
from app.api.endpoints.gamification import router as gamification_router

# Create a central API router
api_router = APIRouter()

# Include all endpoint routers
# Remove prefixes from these routers since they should be included in the router definitions
api_router.include_router(tpr_router)
api_router.include_router(commitment_router)
api_router.include_router(hyperfold_router)
api_router.include_router(bioauth_router)
api_router.include_router(accessibility_router)
api_router.include_router(project_management_router)
api_router.include_router(calendar_integration_router)
api_router.include_router(gamification_router)

# Add more endpoint routers here as they are developed
