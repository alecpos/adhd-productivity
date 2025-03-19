from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.routes.base_routes import BaseRouter
from app.core.responses import APIResponse
from app.utils.decorators import handle_service_error
from app.models.voice_command_model import VoiceCommandModel
from app.schemas.voice_command_schema import (
    VoiceCommandRequestSchema,
    VoiceCommandResponseSchema,
    TaskCreationCommandSchema,
    ReminderCreationCommandSchema,
    VoiceCommandLogSchema,
    VoicePreferencesSchema
)

class VoiceCommandRouter(BaseRouter[VoiceCommandModel, VoiceCommandRequestSchema, VoiceCommandResponseSchema]):
    """Voice command router."""

    def __init__(self):
        super().__init__(
            prefix="/voice",
            tags=["voice"],
            model_class=VoiceCommandModel,
            schema_class=VoiceCommandRequestSchema,
            service_class=VoiceCommandResponseSchema,
        )
        self._register_custom_routes()

    def _register_custom_routes(self):
        @self.router.post("/process", response_model=APIResponse[VoiceCommandResponseSchema])
        @handle_service_error
        async def process_voice_command(
            command: VoiceCommandRequestSchema, db: AsyncSession = Depends(get_db)
        ):
            """Process a voice command."""
            service = self.service_class(db)
            result = await service.process_command(command)
            return APIResponse(data=result, message="Voice command processed successfully")

        @self.router.get("/history", response_model=APIResponse[List[VoiceCommandLogSchema]])
        @handle_service_error
        async def get_command_history(
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None,
            db: AsyncSession = Depends(get_db),
        ):
            """Get voice command history."""
            service = self.service_class(db)
            history = await service.get_command_history(start_date, end_date)
            return APIResponse(data=history, message="Command history retrieved successfully")

        @self.router.put("/preferences", response_model=APIResponse[VoicePreferencesSchema])
        @handle_service_error
        async def update_command_preferences(
            preferences: VoicePreferencesSchema, db: AsyncSession = Depends(get_db)
        ):
            """Update voice command preferences."""
            service = self.service_class(db)
            updated_prefs = await service.update_preferences(preferences)
            return APIResponse(
                data=updated_prefs, message="Command preferences updated successfully"
            )

        @self.router.get("/suggestions", response_model=APIResponse[List[str]])
        @handle_service_error
        async def get_command_suggestions(
            context: Optional[str] = None, db: AsyncSession = Depends(get_db)
        ):
            """Get command suggestions based on context."""
            service = self.service_class(db)
            suggestions = await service.get_suggestions(context)
            return APIResponse(
                data=suggestions, message="Command suggestions retrieved successfully"
            )

        @self.router.post("/train", response_model=APIResponse)
        @handle_service_error
        async def train_voice_model(
            training_data: List[VoiceCommandRequestSchema], db: AsyncSession = Depends(get_db)
        ):
            """Train voice command model with new data."""
            service = self.service_class(db)
            await service.train_model(training_data)
            return APIResponse(data=None, message="Voice model trained successfully")

        @self.router.get("/analytics", response_model=APIResponse)
        @handle_service_error
        async def get_command_analytics(
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None,
            db: AsyncSession = Depends(get_db),
        ):
            """Get voice command analytics."""
            service = self.service_class(db)
            analytics = await service.get_analytics(start_date, end_date)
            return APIResponse(data=analytics, message="Command analytics retrieved successfully")


router = VoiceCommandRouter().router
