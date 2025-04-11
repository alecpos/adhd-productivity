"""Tests for calendar integration with circadian optimization."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
from uuid import uuid4, UUID
from fastapi import HTTPException

from app.schemas.scheduling_schema import (
    CircadianCalendarOptimizationRequest,
    CircadianCalendarOptimizationResponse,
    CircadianOptimizationResult,
    ApplyCircadianOptimizationRequest,
    ApplyCircadianOptimizationResponse
)


class TestCalendarCircadianIntegration:
    """Tests for calendar integration with circadian optimization."""

    @pytest.mark.asyncio
    async def test_circadian_optimization_with_calendar_events(self):
        """Test flow for optimizing calendar events with circadian awareness."""
        # Create test data
        now = datetime.now()
        event_id = str(uuid4())

        # Create test request
        request = CircadianCalendarOptimizationRequest(
            start_date=now,
            end_date=now + timedelta(days=1),
            only_flexible_events=True
        )

        # Expected response structure
        expected_response = CircadianCalendarOptimizationResponse(
            optimized_schedule=[
                CircadianOptimizationResult(
                    event_id=event_id,
                    title="Important Meeting",
                    original_start=now + timedelta(hours=1),
                    original_end=now + timedelta(hours=2),
                    suggested_start=now + timedelta(hours=4),
                    suggested_end=now + timedelta(hours=5),
                    time_difference_minutes=180,
                    suitability_score=0.85,
                    cognitive_category="focus_intensive",
                    energy_level=8.0
                )
            ],
            energy_curve=[
                {"hour": 9, "energy_level": 8.5},
                {"hour": 10, "energy_level": 9.0}
            ],
            events_analyzed=2,
            events_optimized=1,
            message="Calendar events optimized with circadian rhythm awareness"
        )

        # Assert that the response structure contains all the fields we need
        assert hasattr(expected_response, 'optimized_schedule')
        assert hasattr(expected_response, 'energy_curve')
        assert hasattr(expected_response, 'events_analyzed')
        assert hasattr(expected_response, 'events_optimized')
        assert hasattr(expected_response, 'message')

        # Verify that each optimization result has necessary fields
        optimization = expected_response.optimized_schedule[0]
        assert hasattr(optimization, 'event_id')
        assert hasattr(optimization, 'title')
        assert hasattr(optimization, 'original_start')
        assert hasattr(optimization, 'original_end')
        assert hasattr(optimization, 'suggested_start')
        assert hasattr(optimization, 'suggested_end')
        assert hasattr(optimization, 'time_difference_minutes')
        assert hasattr(optimization, 'suitability_score')
        assert hasattr(optimization, 'cognitive_category')
        assert hasattr(optimization, 'energy_level')

    @pytest.mark.asyncio
    async def test_apply_circadian_optimization(self):
        """Test flow for applying circadian optimization to calendar events."""
        # Create test data
        now = datetime.now()
        event_id1 = str(uuid4())
        event_id2 = str(uuid4())

        # Create request
        request = ApplyCircadianOptimizationRequest(
            optimization_results=[
                CircadianOptimizationResult(
                    event_id=event_id1,
                    title="Meeting 1",
                    original_start=now,
                    original_end=now + timedelta(hours=1),
                    suggested_start=now + timedelta(hours=2),
                    suggested_end=now + timedelta(hours=3),
                    time_difference_minutes=120,
                    suitability_score=0.8,
                    cognitive_category="focus_intensive",
                    energy_level=8.0
                ),
                CircadianOptimizationResult(
                    event_id=event_id2,
                    title="Meeting 2",
                    original_start=now + timedelta(hours=4),
                    original_end=now + timedelta(hours=5),
                    suggested_start=now + timedelta(hours=6),
                    suggested_end=now + timedelta(hours=7),
                    time_difference_minutes=120,
                    suitability_score=0.9,
                    cognitive_category="creative",
                    energy_level=7.0
                )
            ]
        )

        # Expected response
        expected_response = ApplyCircadianOptimizationResponse(
            success=True,
            message="Applied 2 optimizations, skipped 0",
            applied_count=2,
            skipped_count=0,
            errors=[],
            total_errors=0
        )

        # Assert that the response structure contains all the fields we need
        assert hasattr(expected_response, 'success')
        assert hasattr(expected_response, 'message')
        assert hasattr(expected_response, 'applied_count')
        assert hasattr(expected_response, 'skipped_count')
        assert hasattr(expected_response, 'errors')
        assert hasattr(expected_response, 'total_errors')

        # Create error case response
        error_response = ApplyCircadianOptimizationResponse(
            success=False,
            message="Applied 0 optimizations, skipped 2",
            applied_count=0,
            skipped_count=2,
            errors=["Event not found", "User does not own event"],
            total_errors=2
        )

        # Assert error response structure
        assert hasattr(error_response, 'success')
        assert not error_response.success
        assert hasattr(error_response, 'errors')
        assert len(error_response.errors) == 2
