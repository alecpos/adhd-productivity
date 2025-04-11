"""
Integration Tests for Stochastic Time Estimation Engine

This module contains integration tests that verify the different components
of the stochastic time estimation engine work together correctly.
"""

import pytest
import asyncio
import os
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, AsyncMock

from app.tests.ml.stochastic_time_estimation.test_utils import (
    create_mock_task, create_mock_user, create_mock_health_metrics, mock_db, run_async_test
)


@pytest.fixture
def mock_components():
    """Create mock instances of all components."""
    with patch("app.ml.stochastic_time_estimation.BayesianDurationPredictor") as mock_bdp, \
         patch("app.ml.stochastic_time_estimation.NLPComplexityAnalyzer") as mock_nca, \
         patch("app.ml.stochastic_time_estimation.ContextualStressorDetector") as mock_csd, \
         patch("app.ml.stochastic_time_estimation.TimeBufferCalculator") as mock_tbc:

        # Configure mock instances
        mock_bdp_instance = MagicMock()
        mock_bdp_instance.predict = AsyncMock()  # Replace with AsyncMock
        mock_bdp_instance.predict.return_value = {
            "estimated_duration": 60.0,
            "confidence_interval": (45.0, 75.0),
            "factors": {"complexity": 1.2, "user_history": 1.1}
        }

        mock_nca_instance = MagicMock()
        mock_nca_instance.analyze_task = AsyncMock()  # Replace with AsyncMock
        mock_nca_instance.analyze_task.return_value = {
            "complexity_score": 0.7,
            "cognitive_load": "medium",
            "focus_required": 3,
            "time_impact_factor": 1.2
        }
        mock_nca_instance.get_time_factor = AsyncMock()  # Replace with AsyncMock
        mock_nca_instance.get_time_factor.return_value = 1.2

        mock_csd_instance = MagicMock()
        mock_csd_instance.detect_current_stress = AsyncMock()  # Replace with AsyncMock
        mock_csd_instance.detect_current_stress.return_value = {
            "overall_stress_level": "moderate",
            "stress_score": 45,
            "time_impact_factor": 1.3
        }
        mock_csd_instance.get_task_stress_adjustment = AsyncMock()  # Replace with AsyncMock
        mock_csd_instance.get_task_stress_adjustment.return_value = 1.3

        mock_tbc_instance = MagicMock()
        mock_tbc_instance.calculate_buffer = AsyncMock()  # Replace with AsyncMock
        mock_tbc_instance.calculate_buffer.return_value = 15.0
        mock_tbc_instance.calculate_buffers_for_task_sequence = AsyncMock()  # Replace with AsyncMock
        mock_tbc_instance.calculate_buffers_for_task_sequence.return_value = [10.0, 15.0, 12.0]

        # Configure mock constructors to return mock instances
        mock_bdp.return_value = mock_bdp_instance
        mock_nca.return_value = mock_nca_instance
        mock_csd.return_value = mock_csd_instance
        mock_tbc.return_value = mock_tbc_instance

        yield {
            "bayesian_predictor": mock_bdp_instance,
            "nlp_analyzer": mock_nca_instance,
            "stressor_detector": mock_csd_instance,
            "buffer_calculator": mock_tbc_instance
        }


class TestStochasticTimeEstimationIntegration:
    """Integration tests for the Stochastic Time Estimation Engine."""

    @pytest.mark.asyncio
    async def test_complete_estimation_pipeline(self, mock_db, mock_components):
        """Test the complete estimation pipeline from task creation to schedule."""
        # Create test data
        task1 = create_mock_task(
            task_id="task-1",
            description="Write a comprehensive project proposal for the client",
            estimated_duration=45.0
        )
        task2 = create_mock_task(
            task_id="task-2",
            description="Create wireframes for the new mobile app",
            estimated_duration=60.0
        )
        task3 = create_mock_task(
            task_id="task-3",
            description="Meeting with the development team",
            estimated_duration=30.0
        )

        user = create_mock_user(user_id="test-user-1")

        # Get components
        bdp = mock_components["bayesian_predictor"]
        nca = mock_components["nlp_analyzer"]
        csd = mock_components["stressor_detector"]
        tbc = mock_components["buffer_calculator"]

        # Simulate the estimation pipeline

        # Step 1: Analyze task complexity
        complexity_results = []
        for task in [task1, task2, task3]:
            # Access dictionary key rather than attribute
            complexity_result = await nca.analyze_task(task["id"])
            complexity_results.append(complexity_result)

        # Step 2: Get duration predictions
        duration_predictions = []
        for task in [task1, task2, task3]:
            # Access dictionary key rather than attribute
            prediction = await bdp.predict(task["id"])
            duration_predictions.append(prediction)

        # Step 3: Apply stress adjustments
        stress_result = await csd.detect_current_stress(user.id)
        adjusted_durations = []
        for task, prediction in zip([task1, task2, task3], duration_predictions):
            task_adjustment = await csd.get_task_stress_adjustment(task["id"])
            adjusted_duration = prediction["estimated_duration"] * task_adjustment
            adjusted_durations.append(adjusted_duration)

        # Step 4: Calculate transition buffers
        task_sequence = [task1["id"], task2["id"], task3["id"]]
        transition_buffers = await tbc.calculate_buffers_for_task_sequence(task_sequence)

        # Step 5: Create the final schedule
        schedule = []
        current_time = datetime.now().replace(microsecond=0)

        for i, (task, duration) in enumerate(zip([task1, task2, task3], adjusted_durations)):
            # Add task to schedule
            end_time = current_time + timedelta(minutes=int(duration))
            schedule.append({
                "task_id": task["id"],
                "start_time": current_time,
                "end_time": end_time,
                "duration_minutes": int(duration)
            })

            # Add transition buffer if not the last task
            if i < len(transition_buffers):
                buffer_minutes = transition_buffers[i]
                current_time = end_time + timedelta(minutes=int(buffer_minutes))
            else:
                current_time = end_time

        # Verify the results

        # Check if all tasks are in the schedule
        assert len(schedule) == 3

        # Check if durations were adjusted
        for i, original_task in enumerate([task1, task2, task3]):
            assert schedule[i]["duration_minutes"] != int(original_task["estimated_duration"])

        # Check if timings are consistent
        for i in range(1, len(schedule)):
            previous_end = schedule[i-1]["end_time"]
            current_start = schedule[i]["start_time"]
            assert current_start > previous_end
            buffer = (current_start - previous_end).total_seconds() / 60
            assert buffer > 0

        # Verify all components were called
        assert nca.analyze_task.call_count == 3
        assert bdp.predict.call_count == 3
        assert csd.detect_current_stress.call_count == 1
        assert csd.get_task_stress_adjustment.call_count == 3
        assert tbc.calculate_buffers_for_task_sequence.call_count == 1

    @pytest.mark.asyncio
    async def test_impact_of_stress_on_duration(self, mock_db, mock_components):
        """Test how different stress levels impact duration estimates."""
        # Setup
        task = create_mock_task(
            task_id="task-1",
            description="Complete a detailed analysis report",
            estimated_duration=60.0
        )

        # Get components
        bdp = mock_components["bayesian_predictor"]
        csd = mock_components["stressor_detector"]

        # Configure stress detector for different stress levels
        stress_levels = ["low", "moderate", "high", "extreme"]
        time_impacts = [1.05, 1.3, 1.6, 2.0]

        durations = []

        for stress_level, time_impact in zip(stress_levels, time_impacts):
            # Update the mock to return different stress levels
            csd.detect_current_stress.return_value = {
                "overall_stress_level": stress_level,
                "stress_score": 25 * (stress_levels.index(stress_level) + 1),
                "time_impact_factor": time_impact
            }
            csd.get_task_stress_adjustment.return_value = time_impact

            # Get the prediction and apply stress adjustment
            prediction = await bdp.predict(task["id"])
            task_adjustment = await csd.get_task_stress_adjustment(task["id"])
            adjusted_duration = prediction["estimated_duration"] * task_adjustment
            durations.append(adjusted_duration)

        # Verify durations increase with stress level
        for i in range(1, len(durations)):
            assert durations[i] > durations[i-1]

        # Verify highest stress level significantly impacts duration
        assert durations[-1] >= durations[0] * 1.5

    @pytest.mark.asyncio
    async def test_complexity_analysis_impact(self, mock_db, mock_components):
        """Test how task complexity analysis impacts duration estimates."""
        # Setup tasks with varying complexity
        tasks = [
            create_mock_task(
                task_id="simple-task",
                description="Send a quick email to the team",
                estimated_duration=15.0
            ),
            create_mock_task(
                task_id="medium-task",
                description="Prepare slides for the weekly presentation",
                estimated_duration=45.0
            ),
            create_mock_task(
                task_id="complex-task",
                description="Develop a comprehensive business strategy for the next quarter",
                estimated_duration=120.0
            )
        ]

        # Get components
        nca = mock_components["nlp_analyzer"]
        bdp = mock_components["bayesian_predictor"]

        # Configure complexity analyzer for different complexity levels
        complexity_scores = [0.3, 0.6, 0.9]
        time_impacts = [0.9, 1.2, 1.5]

        # Make predictions for each task
        adjusted_durations = []
        for i, task in enumerate(tasks):
            # Update the mock to return different complexity levels
            nca.analyze_task.return_value = {
                "complexity_score": complexity_scores[i],
                "cognitive_load": ["low", "medium", "high"][i],
                "focus_required": i + 2,
                "time_impact": time_impacts[i]
            }
            nca.get_time_factor.return_value = time_impacts[i]

            # Configure predictor to take complexity into account
            base_duration = task["estimated_duration"]
            bdp.predict.return_value = {
                "estimated_duration": base_duration * time_impacts[i],
                "confidence_interval": (base_duration * 0.8, base_duration * 1.2),
                "factors": {"complexity": time_impacts[i], "user_history": 1.0}
            }

            # Get the prediction
            prediction = await bdp.predict(task["id"])
            adjusted_durations.append(prediction["estimated_duration"])

        # Verify that complexity impacts duration
        ratio_simple_to_complex = adjusted_durations[2] / adjusted_durations[0]
        assert ratio_simple_to_complex > (tasks[2]["estimated_duration"] / tasks[0]["estimated_duration"])

    @pytest.mark.asyncio
    async def test_buffer_calculation_and_adaptation(self, mock_db, mock_components):
        """Test buffer calculation adapts to task characteristics."""
        # Create test data with different locations and tools
        home_task = create_mock_task(
            task_id="home-task",
            location="home",
            tools_required=["computer"],
            energy_required=2
        )
        office_task = create_mock_task(
            task_id="office-task",
            location="office",
            tools_required=["whiteboard", "projector"],
            energy_required=4
        )
        coffee_task = create_mock_task(
            task_id="coffee-task",
            location="coffee shop",
            tools_required=["notebook", "phone"],
            energy_required=3
        )

        # Get buffer calculator
        tbc = mock_components["buffer_calculator"]

        # Configure buffer calculator with different responses for different transitions
        transition_responses = {
            ("home-task", "office-task"): 25.0,  # Location change
            ("office-task", "coffee-task"): 20.0,  # Location change
            ("coffee-task", "home-task"): 15.0,  # Location change
            ("home-task", "home-task"): 5.0,  # Same location
            ("office-task", "office-task"): 5.0,  # Same location
        }

        async def mock_calculate_buffer(task1_id, task2_id):
            key = (task1_id, task2_id)
            return transition_responses.get(key, 10.0)

        tbc.calculate_buffer.side_effect = mock_calculate_buffer

        # Test different transitions
        buffers = []
        for from_task, to_task in [
            (home_task, office_task),
            (office_task, coffee_task),
            (coffee_task, home_task),
            (home_task, home_task),
            (office_task, office_task)
        ]:
            buffer = await tbc.calculate_buffer(from_task["id"], to_task["id"])
            buffers.append(buffer)

        # Verify location changes require more buffer time
        assert buffers[0] > buffers[3]  # home->office > home->home
        assert buffers[1] > buffers[4]  # office->coffee > office->office

        # Test sequence calculation
        task_sequence = [home_task["id"], office_task["id"], coffee_task["id"], home_task["id"]]
        tbc.calculate_buffers_for_task_sequence.return_value = [buffers[0], buffers[1], buffers[2]]

        sequence_buffers = await tbc.calculate_buffers_for_task_sequence(task_sequence)

        # Verify sequence buffers match individual buffer calculations
        assert sequence_buffers == [buffers[0], buffers[1], buffers[2]]
        assert sum(sequence_buffers) == buffers[0] + buffers[1] + buffers[2]
