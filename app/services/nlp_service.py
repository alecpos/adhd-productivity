"""Natural Language Processing service for text analysis and task parsing."""

from datetime import datetime
from typing import Dict, Any, List, Optional
from uuid import UUID
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.base_service import BaseService
from app.models.nlp_model import NLPModel
from app.schemas.nlp_schema import (
    NLPParserResponseSchema,
    NLPAnalysisSchema,
    NLPTaskParseSchema,
    TaskComplexityAnalysisSchema,
    FocusStrategySchema
)
from app.services.llm_service import LLMService
from app.utils.metrics import ServiceMetrics

logger = logging.getLogger(__name__)

service_metrics = ServiceMetrics('nlp')
llm_service = LLMService()


class NLPService(BaseService[NLPModel, NLPParserResponseSchema, NLPTaskParseSchema]):
    """Service for natural language processing and analysis."""

    def __init__(self, db: AsyncSession):
        """Initialize the NLP service with database session."""
        super().__init__(db)
        self.metrics = service_metrics
        self.llm = llm_service

    async def parse_text(self, text: str, user_id: UUID) -> NLPParserResponseSchema:
        """Parse and analyze text using NLP."""
        try:
            # Extract structured data using LLM
            parsed_data = await self.llm.extract_structured_data(text)

            # Create NLP model instance
            nlp_record = NLPModel(
                user_id=user_id,
                text=text,
                parsed_data=parsed_data,
                confidence_score=parsed_data.get('confidence', 0.0),
                entities=parsed_data.get('entities', []),
                intent=parsed_data.get('intent')
            )

            # Save to database
            self.db.add(nlp_record)
            await self.db.commit()
            await self.db.refresh(nlp_record)

            # Convert to response schema
            return NLPParserResponseSchema.from_orm(nlp_record)

        except Exception as e:
            self.metrics.increment('parse_text.error')
            raise e

    async def get_analysis(self, text_id: UUID, user_id: UUID) -> NLPAnalysisSchema:
        """Get detailed NLP analysis for a previously parsed text."""
        try:
            # Get the NLP record
            query = select(NLPModel).where(
                NLPModel.id == text_id,
                NLPModel.user_id == user_id
            )
            result = await self.db.execute(query)
            nlp_record = result.scalar_one_or_none()

            if not nlp_record:
                raise ValueError(f"No NLP record found for text_id: {text_id}")

            # Perform detailed analysis using LLM
            analysis = await self.llm.analyze_text(nlp_record.text)

            return NLPAnalysisSchema(
                id=UUID(),
                text_id=text_id,
                sentiment_score=analysis.get('sentiment', 0.0),
                complexity_score=analysis.get('complexity', 0.0),
                key_phrases=analysis.get('key_phrases', []),
                topics=analysis.get('topics', []),
                summary=analysis.get('summary'),
                recommendations=analysis.get('recommendations', []),
                meta_data=analysis.get('meta_data', {}),
                created_at=datetime.utcnow()
            )

        except Exception as e:
            self.metrics.increment('get_analysis.error')
            raise e

    async def analyze_task_complexity(self, task_description: str) -> TaskComplexityAnalysisSchema:
        """Analyze task complexity with ADHD-specific insights."""
        try:
            # Get ADHD-specific analysis from LLM
            analysis = await self.llm.analyze_task_complexity(task_description)

            return TaskComplexityAnalysisSchema(
                task_id=UUID(),
                complexity_level=analysis.get('complexity_level', 3),
                time_estimate=analysis.get('time_estimate', 30),
                focus_requirements=analysis.get('focus_requirements', {}),
                potential_challenges=analysis.get('challenges', []),
                breakdown_suggestions=analysis.get('breakdown', []),
                energy_level_recommendation=analysis.get('energy_level', 'medium'),
                adhd_friendly_score=analysis.get('adhd_friendly_score', 0.5)
            )

        except Exception as e:
            self.metrics.increment('analyze_task_complexity.error')
            raise e

    async def generate_focus_strategies(
        self, user_profile: Dict[str, Any], task_type: str
    ) -> List[FocusStrategySchema]:
        """Generate personalized focus strategies based on user profile and task type."""
        try:
            # Get personalized strategies from LLM
            strategies = await self.llm.generate_focus_strategies(user_profile, task_type)

            return [
                FocusStrategySchema(
                    strategy_id=UUID(),
                    task_type=task_type,
                    title=strategy.get('title', ''),
                    description=strategy.get('description', ''),
                    duration=strategy.get('duration', 25),
                    break_intervals=strategy.get('break_intervals', []),
                    environment_setup=strategy.get('environment', []),
                    tools_needed=strategy.get('tools', []),
                    effectiveness_rating=None,
                    user_notes=None
                )
                for strategy in strategies
            ]

        except Exception as e:
            self.metrics.increment('generate_focus_strategies.error')
            raise e

    async def process_text(self, text: str) -> Optional[str]:
        """Process text using available NLP services."""
        if not self.llm.is_model_available():
            logger.warning("LLM service not available, using fallback processing")
            return self._fallback_processing(text)

        return await self.llm.generate_text(text)

    def _fallback_processing(self, text: str) -> str:
        """Fallback text processing when LLM is not available."""
        # Implement simple fallback logic
        return f"Processed without LLM: {text}"
