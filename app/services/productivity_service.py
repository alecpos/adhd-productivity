from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, TypedDict
from uuid import UUID
import numpy as np
from scipy import stats
from collections import defaultdict
from sqlalchemy import and_, select

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.energy_model import EnergyLog as EnergyLogModelSchema
from app.models.focus_model import FocusSessionType as FocusSessionTypeSchema, FocusSessionModel
from app.schemas.productivity_schema import ProductivityInsights, ProductivityInsightsSchema
from app.services.base_service import BaseService


class InterruptionDict(TypedDict, total=False):
    """Type definition for interruption dictionary."""
    reason: str
    duration: int
    timestamp: datetime
    impact: int


class ProductivityService(BaseService):
    async def track_energy(self, user_id: UUID, energy_level: EnergyLogModelSchema, timestamp: datetime, notes: Optional[str]=None, activity_type: Optional[str]=None) -> EnergyLogModelSchema:
        """Track user's energy levels and associated activities."""
        async with self.error_handler('tracking energy'):
            energy_log = EnergyLogModelSchema(user_id=user_id, energy_level=energy_level, timestamp=timestamp, notes=notes, activity_type=activity_type)
            self.db.add(energy_log)
            await self.db.commit()
            await self.db.refresh(energy_log)
            self._invalidate_cache(f'energy_patterns_{user_id}')
            return energy_log

    async def start_focus_session(self, user_id: UUID, session_type: FocusSessionTypeSchema, purpose: Optional[str]=None, environment: Optional[str]=None) -> FocusSessionModel:
        """Start a focus session with validation."""
        async with self.error_handler('starting focus session'):
            active_session = await self._get_active_session(user_id)
            if active_session:
                raise ValueError('User already has an active session')
            session = FocusSessionModel(
                user_id=user_id,
                start_time=datetime.now(timezone.utc),
                session_type=session_type,
                purpose=purpose,
                environment=environment,
                metrics={'planned_duration': 0, 'interruptions': []}
            )
            self.db.add(session)
            await self.db.commit()
            await self.db.refresh(session)
            self._invalidate_cache(f'focus_sessions_{user_id}')
            return session

    async def end_focus_session(self, user_id: UUID, session_id: UUID, interruptions: Optional[List[InterruptionDict]]=None) -> FocusSessionModel:
        """End a focus session and record metrics."""
        async with self.error_handler('ending focus session'):
            session = await self.db.execute(
                select(FocusSessionModel).where(
                    and_(
                        FocusSessionModel.id == session_id,
                        FocusSessionModel.user_id == user_id
                    )
                )
            )
            session = session.scalar_one_or_none()
            if not session:
                raise ValueError('Session not found')
            session.end_time = datetime.now(timezone.utc)
            if interruptions:
                session.metrics['interruptions'] = interruptions
            session.metrics['actual_duration'] = (session.end_time - session.start_time).total_seconds() / 60
            await self.db.commit()
            await self.db.refresh(session)
            self._invalidate_cache(f'focus_sessions_{user_id}')
            return session

    async def get_productivity_insights(self, user_id: UUID, start_date: datetime, end_date: datetime) -> ProductivityInsightsSchema:
        """Generate comprehensive productivity insights."""
        async with self.error_handler('generating productivity insights'):
            self.validate_date_range(start_date, end_date)
            cache_key = f'insights_{user_id}_{start_date.date()}_{end_date.date()}'
            cached_insights = self._get_cached_data(cache_key)
            if cached_insights:
                return cached_insights
            energy_patterns = await self._analyze_energy_patterns(user_id, start_date, end_date)
            focus_analytics = await self._analyze_focus_sessions(user_id, start_date, end_date)
            recommendations = self._generate_recommendations(energy_patterns, focus_analytics)
            insights = ProductivityInsights(
                optimal_focus_times=self._calculate_optimal_times(energy_patterns, focus_analytics),
                energy_patterns=energy_patterns['patterns'],
                recommendations=recommendations,
                focus_session_stats=focus_analytics['stats']
            )
            self._cache_data(cache_key, insights)
            return insights

    async def _analyze_energy_patterns(self, user_id: UUID, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze energy patterns with advanced metrics."""
        logs = await self.db.execute(
            select(EnergyLogModelSchema).where(
                and_(
                    EnergyLogModelSchema.user_id == user_id,
                    EnergyLogModelSchema.timestamp >= start_date,
                    EnergyLogModelSchema.timestamp <= end_date
                )
            )
        )
        logs = logs.scalars().all()
        if not logs:
            return {'patterns': {}, 'metrics': {}}
        patterns = self._calculate_energy_patterns(logs)
        energy_levels = [log.energy_level.value for log in logs]
        variability = np.std(energy_levels)
        x = np.arange(len(energy_levels))
        slope, _, r_value, _, _ = stats.linregress(x, energy_levels)
        return {
            'patterns': patterns,
            'metrics': {
                'variability': round(variability, 2),
                'trend': round(slope, 2),
                'trend_strength': round(abs(r_value), 2)
            }
        }

    async def _analyze_focus_sessions(self, user_id: UUID, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze focus sessions with detailed metrics."""
        sessions = await self.db.execute(
            select(FocusSessionModel).where(
                and_(
                    FocusSessionModel.user_id == user_id,
                    FocusSessionModel.start_time >= start_date,
                    FocusSessionModel.start_time <= end_date
                )
            )
        )
        sessions = sessions.scalars().all()
        if not sessions:
            return {'stats': {}, 'patterns': {}}
        completed_sessions = [s for s in sessions if s.end_time]
        total_duration = sum(((s.end_time - s.start_time).total_seconds() / 3600 for s in completed_sessions))
        avg_duration = total_duration / len(completed_sessions) if completed_sessions else 0
        interruption_stats = self._analyze_interruptions(completed_sessions)
        success_patterns = self._calculate_success_patterns(completed_sessions)
        return {
            'stats': {
                'total_hours': round(total_duration, 2),
                'average_session_length': round(avg_duration, 2),
                'completion_rate': round(len(completed_sessions) / len(sessions), 2),
                'interruption_rate': interruption_stats['rate'],
                'most_productive_environment': success_patterns.get('best_environment', 'unknown')
            },
            'patterns': success_patterns
        }

    async def _get_active_session(self, user_id: UUID) -> Optional[FocusSessionModel]:
        """Get user's active focus session."""
        result = await self.db.execute(
            select(FocusSessionModel).where(
                and_(
                    FocusSessionModel.user_id == user_id,
                    FocusSessionModel.end_time.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    def _analyze_interruptions(self, sessions: List[FocusSessionModel]) -> Dict[str, Any]:
        """Analyze interruption patterns in focus sessions."""
        total_interruptions = sum((len(s.metrics.get('interruptions', [])) for s in sessions))
        return {
            'rate': round(total_interruptions / len(sessions), 2) if sessions else 0,
            'patterns': self._calculate_interruption_patterns(sessions)
        }

    def _calculate_interruption_patterns(self, sessions: List[FocusSessionModel]) -> Dict[str, Any]:
        """Calculate detailed interruption patterns."""
        patterns = defaultdict(int)
        for session in sessions:
            for interruption in session.metrics.get('interruptions', []):
                if isinstance(interruption, dict) and 'reason' in interruption:
                    patterns[interruption['reason']] += 1
        return dict(sorted(patterns.items(), key=lambda x: x[1], reverse=True))

    def _calculate_success_patterns(self, sessions: List[FocusSessionModel]) -> Dict[str, Any]:
        """Calculate success patterns from completed sessions."""
        if not sessions:
            return {'best_environment': None, 'patterns': {}}

        environment_scores = defaultdict(list)
        for session in sessions:
            if session.environment and hasattr(session, 'effectiveness_score'):
                environment_scores[session.environment].append(session.effectiveness_score)

        best_environment = max(
            environment_scores.items(),
            key=lambda x: sum(x[1]) / len(x[1]) if x[1] else 0,
            default=(None, [])
        )[0]

        return {
            'best_environment': best_environment,
            'environment_scores': {env: sum(scores) / len(scores) for env, scores in environment_scores.items()}
        }

    def _calculate_optimal_times(self, energy_patterns: Dict[str, Any], focus_analytics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calculate optimal focus times based on energy and focus patterns."""
        # Implementation for calculating optimal times
        return []

    def _generate_recommendations(self, energy_patterns: Dict[str, Any], focus_analytics: Dict[str, Any]) -> List[str]:
        """Generate personalized recommendations based on patterns."""
        # Implementation for generating recommendations
        return []

    def validate_date_range(self, start_date: datetime, end_date: datetime) -> None:
        """Validate the date range for analysis."""
        if start_date > end_date:
            raise ValueError("Start date must be before end date")
        if (end_date - start_date).days > 90:
            raise ValueError("Date range cannot exceed 90 days")
