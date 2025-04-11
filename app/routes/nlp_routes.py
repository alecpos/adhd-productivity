"""Natural Language Processing routes for text analysis and parsing."""

import logging
from typing import Dict, Any, List
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.auth_service import get_current_user
from app.schemas.user_schema import UserSchema, User
from app.schemas.nlp_schema import (
    NLPParserResponseSchema,
    NLPParserRequestSchema,
    NLPAnalysisSchema,
)
from app.schemas.task_schema import TaskCreate
from app.services.nlp_service import NLPService
from app.services.task_service import TaskService
from app.routes.base_routes import BaseRouter
from app.models.nlp_model import NLPModel
from app.core.responses import APIResponse
from app.core.nlp_parser import NLPParser


class NLPParserRouter(BaseRouter[NLPParserResponseSchema, NLPService, NLPModel]):
    """Router for NLP parsing and analysis endpoints."""

    def __init__(self):
        """Initialize the router with NLP routes."""
        super().__init__(
            prefix="/nlp",
            tags=["nlp"],
            schema_class=NLPParserResponseSchema,
            service_class=NLPService,
            model_class=NLPModel,
        )
        self._register_custom_routes()

    def _register_custom_routes(self):
        """Register custom routes for NLP endpoints."""

        @self.router.post("/parse", response_model=APIResponse[NLPParserResponseSchema])
        async def parse_text(
            request: NLPParserRequestSchema,
            current_user: UserSchema = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Parse and analyze text using NLP."""
            try:
                service = self.service_class(db)
                result = await service.parse_text(request.text, current_user.id)
                return APIResponse(data=result, message="Text parsed successfully")
            except Exception as e:
                logger.error(f"Error parsing text: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
                )

        @self.router.get("/analysis/{text_id}", response_model=APIResponse[NLPAnalysisSchema])
        async def get_analysis(
            text_id: UUID,
            current_user: UserSchema = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Get detailed NLP analysis for a previously parsed text."""
            try:
                service = self.service_class(db)
                analysis = await service.get_analysis(text_id, current_user.id)
                return APIResponse(data=analysis, message="Analysis retrieved successfully")
            except Exception as e:
                logger.error(f"Error retrieving analysis: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
                )


logger = logging.getLogger(__name__)
router = NLPParserRouter().router


@router.post("/nlp-to-task", response_model=TaskCreate)
async def nlp_to_task(command: str, user_id: str, db: AsyncSession = Depends(get_db)):
    """
    Process NLP command into actionable tasks, subtasks, and recurring schedules.
    """
    try:
        task_data = await NLPParser.parse(command)
        subtasks = []
        if "subtasks" in task_data:
            for subtask in task_data["subtasks"]:
                subtasks.append(await TaskService.create_task(db, user_id=user_id, **subtask))
        task = await TaskService.create_task(db, user_id=user_id, **task_data)
        if subtasks:
            for subtask in subtasks:
                subtask.parent_id = task.id
                await db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing NLP command: {str(e)}")


@router.post("/analyze-task")
async def analyze_task(
    task_description: str, current_user: User = Depends(get_current_user)
) -> dict:
    """
    Analyze a task using DeepSeek-R1 for ADHD-specific insights
    """
    try:
        return await llm_service.analyze_task_complexity(task_description)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/focus-strategies")
async def get_focus_strategies(
    task_type: str, current_user: User = Depends(get_current_user)
) -> List[str]:
    """ """
    try:
        user_profile = {
            "performance_history": current_user.performance_metrics,
            "preferences": current_user.adhd_settings,
            "energy_patterns": current_user.energy_patterns,
        }
        return await llm_service.generate_focus_strategies(user_profile, task_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
