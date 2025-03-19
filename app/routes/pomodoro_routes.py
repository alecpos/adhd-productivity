from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.routes.base_routes import BaseRouter
from app.schemas.pomodoro_schema import (
    PomodoroSchema,
    PomodoroCreateSchema,
    PomodoroResponseSchema,
    PomodoroUpdateSchema,
)
from app.services.pomodoro_service import PomodoroService


class PomodoroRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            prefix="/pomodoro",
            tags=["pomodoro"],
            schema_class=PomodoroResponseSchema,
            service_class=PomodoroService,
            model_class=PomodoroSchema,
        )
        self._register_custom_routes()

    def _register_custom_routes(self):
        """Register custom routes specific to Pomodoro functionality."""

        @self.router.post("/start", response_model=PomodoroResponseSchema)
        async def start_session(
            session_data: PomodoroCreateSchema,
            db: AsyncSession = Depends(get_db),
        ):
            service = PomodoroService(db)
            return await service.start_session(session_data)

        @self.router.post("/{session_id}/end", response_model=PomodoroResponseSchema)
        async def end_session(session_id: str, db: AsyncSession = Depends(get_db)):
            service = PomodoroService(db)
            return await service.end_session(session_id)

        @self.router.get("/{session_id}/status", response_model=PomodoroResponseSchema)
        async def get_session_status(session_id: str, db: AsyncSession = Depends(get_db)):
            service = PomodoroService(db)
            return await service.get_session_status(session_id)


router = PomodoroRouter().router
