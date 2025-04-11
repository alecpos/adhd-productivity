"""Gamification service module."""

from uuid import UUID
from typing import Dict, Any, List, Optional
import sqlalchemy.exc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from datetime import datetime, timezone, timedelta
import logging
import asyncio
from fastapi import Depends

from app.services.base_service import BaseService
from app.models.gamification_model import StreakModel, PointsModel, BadgeModel, AchievementModel, LeaderboardModel
from app.schemas.gamification_schema import StreakResponse, PointsResponse
from app.core.exceptions import NotFoundException, ServiceError
from app.utils.decorators import handle_service_error, with_concurrency_control
from app.database import get_db

logger = logging.getLogger(__name__)

class GamificationService(BaseService[StreakModel, StreakResponse, PointsResponse]):
    """Service for managing gamification features."""

    def __init__(self, db: AsyncSession):
        """Initialize the service with database session."""
        super().__init__(db=db, model=StreakModel, response_schema=StreakResponse)

    async def get_user_points(self, user_id: UUID) -> Dict[str, Any]:
        """Get points for a user."""
        query = select(PointsModel).where(PointsModel.user_id == user_id)
        result = await self.db.execute(query)
        try:
            points = result.scalar_one_or_none()
        except sqlalchemy.exc.MultipleResultsFound:
            query = select(PointsModel).where(PointsModel.user_id == user_id)
            result = await self.db.execute(query)
            all_points = result.scalars().all()
            total_points = sum((p.total_points for p in all_points))
            points = max(all_points, key=lambda p: p.updated_at)
            points.total_points = total_points
            points.level = self._calculate_level(total_points)
            points.updated_at = datetime.utcnow()
            for p in all_points:
                if p != points:
                    await self.db.delete(p)
            await self.db.commit()
        if not points:
            points = PointsModel(user_id=user_id, total_points=0, level=1, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
            self.db.add(points)
            await self.db.commit()
        return {'total_points': points.total_points, 'level': points.level, 'message': 'Points retrieved successfully'}

    @with_concurrency_control(max_retries=3, retry_exceptions=(Exception,), error_message='Failed to update user points due to concurrent modification')
    async def add_user_points(self, user_id: UUID, points_to_add: int) -> Dict[str, Any]:
        """Add points to a user."""
        query = select(PointsModel).where(PointsModel.user_id == user_id).with_for_update(nowait=True)
        result = await self.db.execute(query)
        points_list = result.scalars().all()
        if len(points_list) > 1:
            total_points = sum((p.total_points for p in points_list))
            points = points_list[0]
            points.total_points = total_points + points_to_add
            points.level = self._calculate_level(points.total_points)
            points.updated_at = datetime.utcnow()
            for p in points_list[1:]:
                await self.db.delete(p)
        elif len(points_list) == 1:
            points = points_list[0]
            points.total_points += points_to_add
            points.level = self._calculate_level(points.total_points)
            points.updated_at = datetime.utcnow()
        else:
            points = PointsModel(user_id=user_id, total_points=points_to_add, level=self._calculate_level(points_to_add), created_at=datetime.utcnow(), updated_at=datetime.utcnow())
            self.db.add(points)
        leaderboard_query = select(LeaderboardModel).where(and_(LeaderboardModel.user_id == user_id, LeaderboardModel.category == 'daily')).with_for_update(nowait=True)
        leaderboard_result = await self.db.execute(leaderboard_query)
        leaderboard_entries = leaderboard_result.scalars().all()
        if not leaderboard_entries:
            leaderboard_entry = LeaderboardModel(user_id=user_id, category='daily', score=float(points.total_points), rank=0, timestamp=datetime.utcnow(), created_at=datetime.utcnow(), updated_at=datetime.utcnow())
            self.db.add(leaderboard_entry)
        else:
            leaderboard_entries.sort(key=lambda x: x.score, reverse=True)
            leaderboard_entry = leaderboard_entries[0]
            leaderboard_entry.score = float(points.total_points)
            leaderboard_entry.updated_at = datetime.utcnow()
            if len(leaderboard_entries) > 1:
                for entry in leaderboard_entries[1:]:
                    await self.db.delete(entry)
        await self.db.commit()
        achievements = await self._check_point_achievements(user_id, points.total_points)
        return {'total_points': points.total_points, 'level': points.level, 'achievements': achievements, 'message': 'Points updated successfully'}

    def _calculate_level(self, total_points: int) -> int:
        """Calculate user level based on total points."""
        if total_points < 100:
            return 1
        return int((total_points / 100) ** 0.5) + 1

    async def update_user_streak(self, user_id: UUID) -> Dict[str, Any]:
        """Update a user's streak."""
        query = select(StreakModel).where(and_(StreakModel.user_id == user_id, StreakModel.streak_type == 'daily'))
        result = await self.db.execute(query)
        streak = result.scalar_one_or_none()
        now = datetime.now(timezone.utc)
        if not streak:
            streak = StreakModel(user_id=user_id, streak_type='daily', current_streak=1, longest_streak=1, last_activity=now, created_at=now, updated_at=now)
            self.db.add(streak)
        else:
            if now - streak.last_activity <= timedelta(hours=24):
                streak.current_streak += 1
                if streak.current_streak > streak.longest_streak:
                    streak.longest_streak = streak.current_streak
            else:
                streak.current_streak = 1
            streak.last_activity = now
            streak.updated_at = now
        await self.db.commit()
        badges = []
        streak_milestones = [3, 7, 14, 30, 60, 90]
        for milestone in streak_milestones:
            if streak.current_streak >= milestone:
                badge = await self._award_streak_badge(user_id, milestone)
                if badge:
                    badges.append(badge)
        return {'current_streak': streak.current_streak, 'longest_streak': streak.longest_streak, 'badges': badges}

    async def _award_streak_badge(self, user_id: UUID, milestone: int) -> Optional[Dict[str, Any]]:
        """Award a streak milestone badge if not already awarded."""
        badge_names = {3: 'StreakModel Starter', 7: 'Weekly Warrior', 14: 'Fortnight Fighter', 30: 'Monthly Master', 60: 'StreakModel Sage', 90: 'StreakModel Legend'}
        badge_name = badge_names.get(milestone)
        if not badge_name:
            query = select(BadgeModel).where(and_(BadgeModel.user_id == user_id, BadgeModel.name == badge_name))
            result = await self.db.execute(query)
            existing_badge = result.scalar_one_or_none()
            if not existing_badge:
                badge = BadgeModel(user_id=user_id, name=badge_name, description=f'Maintained a {milestone}-day streak!', category='streak', level=milestone // 3, earned_at=datetime.now(timezone.utc), meta_data={'milestone': milestone})
                self.db.add(badge)
                await self.db.commit()
                points_to_award = milestone * 10
                await self.add_user_points(user_id, points_to_award)
                return {'name': badge.name, 'description': badge.description, 'points_awarded': points_to_award}

    async def get_leaderboard(self, category: str) -> Dict[str, Any]:
        """Get the leaderboard for a specific category."""
        query = select(LeaderboardModel).where(LeaderboardModel.category == category).order_by(desc(LeaderboardModel.score))
        result = await self.db.execute(query)
        entries = result.scalars().all()
        return {'category': category, 'leaderboard': [{'user_id': str(entry.user_id), 'score': entry.score, 'rank': entry.rank} for entry in entries]}

    async def add_user_to_leaderboard(self, category: str, user_id: UUID) -> Dict[str, Any]:
        """Add a user to the leaderboard."""
        query = select(LeaderboardModel).where(and_(LeaderboardModel.user_id == user_id, LeaderboardModel.category == category)).with_for_update(nowait=True)
        try:
            result = await self.db.execute(query)
            entries = result.scalars().all()
            if entries:
                entries.sort(key=lambda x: x.score, reverse=True)
                existing_entry = entries[0]
                if len(entries) > 1:
                    for entry in entries[1:]:
                        await self.db.delete(entry)
                    await self.db.commit()
                return {'user_id': str(user_id), 'score': existing_entry.score, 'rank': existing_entry.rank, 'message': 'User already in leaderboard'}
            new_entry = LeaderboardModel(user_id=user_id, category=category, score=0.0, rank=1)
            self.db.add(new_entry)
            await self.db.commit()
            await self._update_leaderboard_ranks(category)
            return {'user_id': str(user_id), 'score': new_entry.score, 'rank': new_entry.rank, 'message': 'User added to leaderboard successfully'}
        except Exception as e:
            await self.db.rollback()
            if 'could not obtain lock' in str(e):
                await asyncio.sleep(0.1)
                result = await self.db.execute(select(LeaderboardModel).where(and_(LeaderboardModel.user_id == user_id, LeaderboardModel.category == category)))
                entries = result.scalars().all()
                if entries:
                    entries.sort(key=lambda x: x.score, reverse=True)
                    existing_entry = entries[0]
                    return {'user_id': str(user_id), 'score': existing_entry.score, 'rank': existing_entry.rank, 'message': 'User already in leaderboard'}
            raise ServiceError('Failed to add user to leaderboard')

    async def _update_leaderboard_ranks(self, category: str) -> None:
        """Update ranks for all entries in a leaderboard category."""
        query = select(LeaderboardModel).where(LeaderboardModel.category == category).order_by(desc(LeaderboardModel.score))
        result = await self.db.execute(query)
        entries = result.scalars().all()
        current_rank = 1
        current_score = None
        same_score_count = 0
        for entry in entries:
            if entry.score != current_score:
                current_rank += same_score_count
                same_score_count = 0
                current_score = entry.score
            entry.rank = current_rank
            same_score_count += 1
        await self.db.commit()

    async def get_user_dashboard(self, user_id: UUID) -> Dict[str, Any]:
        """Get the user's dashboard data."""
        try:
            streak_query = select(StreakModel).where(and_(StreakModel.user_id == user_id, StreakModel.streak_type == 'daily'))
            streak_result = await self.db.execute(streak_query)
            streak = streak_result.scalar_one_or_none()
            leaderboard_query = select(LeaderboardModel).where(LeaderboardModel.user_id == user_id)
            leaderboard_result = await self.db.execute(leaderboard_query)
            leaderboard_entries = leaderboard_result.scalars().all()
            points = await self.get_user_points(user_id)
            badges = await self.get_user_badges(user_id)
            achievements = await self.get_user_achievements(user_id)
            streak_data = None
            if streak:
                streak_data = {'user_id': str(streak.user_id), 'streak_type': streak.streak_type, 'current_streak': streak.current_streak, 'longest_streak': streak.longest_streak, 'last_activity': streak.last_activity.isoformat() if streak.last_activity else None}
            points_data = {'total_points': points.get('total_points', 0), 'level': points.get('level', 1), 'message': points.get('message', 'No points data available')}
            return {'streaks': streak_data, 'leaderboard': {'entries': [{'category': entry.category, 'score': entry.score, 'rank': entry.rank} for entry in leaderboard_entries] if leaderboard_entries else []}, 'points': points_data, 'badges': badges or [], 'achievements': achievements or []}
        except Exception as e:
            logger.error(f'Error getting user dashboard: {str(e)}')
            await self.db.rollback()
            raise ServiceError(f'Failed to get user dashboard: {str(e)}')

    async def get_user_badges(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Get all badges for a user."""
        query = select(BadgeModel).where(BadgeModel.user_id == user_id)
        result = await self.db.execute(query)
        badges = result.scalars().all()
        return [{'id': str(badge.id), 'user_id': str(badge.user_id), 'name': badge.name, 'description': badge.description, 'category': badge.category, 'level': badge.level, 'earned_at': badge.earned_at.isoformat(), 'meta_data': badge.meta_data} for badge in badges]

    async def get_user_achievements(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Get all achievements for a user."""
        query = select(AchievementModel).where(AchievementModel.user_id == user_id)
        result = await self.db.execute(query)
        achievements = result.scalars().all()
        return [{'id': str(achievement.id), 'user_id': str(achievement.user_id), 'name': achievement.name, 'description': achievement.description, 'category': achievement.category, 'points': achievement.points, 'earned_at': achievement.earned_at.isoformat(), 'meta_data': achievement.meta_data} for achievement in achievements]

    async def _award_points_achievement(self, user_id: UUID, milestone: int) -> Optional[Dict[str, Any]]:
        """Award a points milestone achievement if not already awarded."""
        achievement_names = {100: 'Point Collector', 500: 'Point Gatherer', 1000: 'Point Master', 5000: 'Point Champion', 10000: 'Point Legend'}
        achievement_name = achievement_names.get(milestone)
        if not achievement_name:
            query = select(AchievementModel).where(and_(AchievementModel.user_id == user_id, AchievementModel.name == achievement_name))
            result = await self.db.execute(query)
            existing_achievement = result.scalar_one_or_none()
            if not existing_achievement:
                achievement = AchievementModel(user_id=user_id, name=achievement_name, description=f'Earned {milestone} total points!', category='points', points=milestone // 10, earned_at=datetime.now(timezone.utc), meta_data={'milestone': milestone, 'progress': 100, 'completed': True})
                self.db.add(achievement)
                await self.db.commit()
                return {'name': achievement.name, 'description': achievement.description, 'bonus_points': achievement.points}

    async def _award_level_achievement(self, user_id: UUID, level: int) -> Optional[Dict[str, Any]]:
        """Award a level up achievement."""
        achievement_name = f'level_{level}'
        query = select(AchievementModel).where(and_(AchievementModel.user_id == user_id, AchievementModel.name == achievement_name))
        result = await self.db.execute(query)
        existing_achievement = result.scalar_one_or_none()
        if not existing_achievement:
            achievement = AchievementModel(user_id=user_id, name=achievement_name, description=f'Reached level {level}!', category='level', points=level * 50, earned_at=datetime.now(timezone.utc), meta_data={'level': level})
            self.db.add(achievement)
            await self.db.commit()
            return {'name': achievement.name, 'description': achievement.description, 'bonus_points': achievement.points}

    async def _check_point_achievements(self, user_id: UUID, total_points: int) -> List[Dict[str, Any]]:
        """Check and award achievements based on point milestones."""
        achievements = []
        point_milestones = [100, 500, 1000, 5000, 10000]
        for milestone in point_milestones:
            if total_points >= milestone:
                achievement = await self._award_points_achievement(user_id, milestone)
                if achievement:
                    achievements.append(achievement)
        level = self._calculate_level(total_points)
        level_milestones = [5, 10, 25, 50, 100]
        if level in level_milestones:
            achievement = await self._award_level_achievement(user_id, level)
            if achievement:
                achievements.append(achievement)

    @handle_service_error
    async def update_leaderboard_score(self, category: str, user_id: UUID, score: float) -> Dict[str, Any]:
        """Update a user's score on the leaderboard."""
        logger.info(f'Updating leaderboard score for user {user_id} in category {category}')
        max_retries = 3
        retry_count = 0
        while retry_count < max_retries:
            try:
                query = select(LeaderboardModel).where(and_(LeaderboardModel.user_id == user_id, LeaderboardModel.category == category)).with_for_update(nowait=True)
                result = await self.db.execute(query)
                entries = result.scalars().all()
                if not entries:
                    raise NotFoundException(f'User {user_id} not found in {category} leaderboard')
                entries.sort(key=lambda x: x.score, reverse=True)
                leaderboard_entry = entries[0]
                if len(entries) > 1:
                    for entry in entries[1:]:
                        await self.db.delete(entry)
                leaderboard_entry.score = score
                leaderboard_entry.updated_at = datetime.now(timezone.utc)
                self.db.add(leaderboard_entry)
                await self.db.commit()
                await self.db.refresh(leaderboard_entry)
                await self._update_leaderboard_ranks(category)
                return {'message': 'Score updated successfully', 'user_id': str(user_id), 'category': category, 'score': score, 'rank': leaderboard_entry.rank}
            except Exception as e:
                await self.db.rollback()
                if isinstance(e, sqlalchemy.exc.DBAPIError) and 'could not obtain lock' in str(e) or (isinstance(e, sqlalchemy.exc.OperationalError) and 'could not obtain lock' in str(e)):
                    if retry_count < max_retries - 1:
                        retry_count += 1
                        await asyncio.sleep(0.1 * retry_count)
                        continue
                raise ServiceError('Failed to update leaderboard score')

def get_gamification_service(db: AsyncSession = Depends(get_db)) -> GamificationService:
    """Get a GamificationService instance with database dependency."""
    return GamificationService(db)
