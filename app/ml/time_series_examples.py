#!/usr/bin/env python
"""
Example script demonstrating the weekly resampling analysis for task transitions.

This script shows how to use the TimeBufferCalculator's weekly_resampling method
to analyze historical task transition data and identify patterns.
"""

import asyncio
import json
import os
import sys
import logging
from datetime import datetime, timedelta
from uuid import uuid4

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the TimeBufferCalculator
from app.ml.stochastic_time_estimation.time_buffer_calculator import TimeBufferCalculator


# Function to generate sample transition data
def generate_sample_transition_data(user_id, num_days=60, transitions_per_day=5):
    """
    Generate sample transition data for demonstration purposes.

    Args:
        user_id: ID of the user
        num_days: Number of days of historical data to generate
        transitions_per_day: Average number of transitions per day

    Returns:
        List of transition records
    """
    import random
    import numpy as np

    transitions = []

    # Create a fixed set of tasks
    task_ids = [str(uuid4()) for _ in range(10)]

    # Create a pattern where transitions are generally harder on Mondays
    # and get easier as the week progresses
    weekday_multipliers = {
        0: 1.3,  # Monday
        1: 1.1,  # Tuesday
        2: 1.0,  # Wednesday
        3: 0.9,  # Thursday
        4: 0.8,  # Friday
        5: 1.2,  # Saturday
        6: 1.1   # Sunday
    }

    # Create a pattern where transitions get better over time
    # (as the user improves their transition skills)
    improvement_factor = 0.995  # Slight improvement each day

    # Base transition time in minutes
    base_transition_time = 15

    end_date = datetime.now()
    start_date = end_date - timedelta(days=num_days)

    current_date = start_date
    while current_date <= end_date:
        # Number of transitions for this day (add some randomness)
        day_transitions = max(1, int(transitions_per_day + random.randint(-2, 2)))

        # Get weekday (0 = Monday, 6 = Sunday)
        weekday = current_date.weekday()
        weekday_multiplier = weekday_multipliers[weekday]

        # Calculate improvement based on how many days have passed
        days_passed = (current_date - start_date).days
        time_improvement = improvement_factor ** days_passed

        for _ in range(day_transitions):
            # Randomly select tasks
            from_task = random.choice(task_ids)
            to_task = random.choice([t for t in task_ids if t != from_task])

            # Calculate transition time with some randomness
            predicted_minutes = int(base_transition_time)

            # Actual minutes includes weekday effect and improvement over time
            actual_minutes = int(base_transition_time * weekday_multiplier * time_improvement)

            # Add some random variance (±30%)
            actual_minutes = int(actual_minutes * random.uniform(0.7, 1.3))

            # Create a timestamp within the day
            hour = random.randint(9, 17)  # Business hours
            minute = random.randint(0, 59)
            timestamp = current_date.replace(hour=hour, minute=minute)

            transition = {
                "user_id": user_id,
                "from_task_id": from_task,
                "to_task_id": to_task,
                "predicted_minutes": predicted_minutes,
                "actual_minutes": actual_minutes,
                "timestamp": timestamp.isoformat(),
                "context_score": random.uniform(0.5, 1.5),
                "difficulty_level": random.choice(["easy", "moderate", "difficult"])
            }

            transitions.append(transition)

        # Move to next day
        current_date += timedelta(days=1)

    return transitions


# Mock database session for demonstration
class MockSession:
    """Mock database session for demonstration purposes."""

    def __init__(self, transition_data):
        self.transition_data = transition_data

    async def execute(self, query):
        """Mock query execution that returns the sample data."""
        return MockResult(self.transition_data)

    async def commit(self):
        """Mock commit that does nothing."""
        pass


class MockResult:
    """Mock query result."""

    def __init__(self, data):
        self.data = data

    def scalars(self):
        """Return mock scalar results."""
        return self

    def first(self):
        """Return first result."""
        return self.data[0] if self.data else None

    def all(self):
        """Return all results."""
        return self.data


async def run_example():
    """Run the weekly resampling example."""

    # Generate a user ID
    user_id = str(uuid4())

    # Generate sample transition data
    logger.info("Generating sample transition data...")
    transitions = generate_sample_transition_data(user_id, num_days=90, transitions_per_day=5)
    logger.info(f"Generated {len(transitions)} sample transitions")

    # Create a TimeBufferCalculator instance with the mock session
    calculator = TimeBufferCalculator()

    # Monkey patch the _get_transition_history method to use our sample data
    async def mock_get_transition_history(self, user_id):
        return transitions

    # Apply the monkey patch
    TimeBufferCalculator._get_transition_history = mock_get_transition_history

    # Run the weekly resampling analysis
    logger.info("Running weekly resampling analysis...")
    result = await calculator.weekly_resampling(
        user_id=user_id,
        lookback_days=90,
        rolling_window_days=7,
        include_weekends=True
    )

    # Display the results
    logger.info("Weekly resampling analysis completed")

    # Display summary statistics
    print("\n=== Weekly Transition Time Analysis ===")
    print(f"Total weeks analyzed: {result['weekly_stats']['total_weeks']}")
    print(f"Average transitions per week: {result['weekly_stats']['average_transitions_per_week']:.2f}")
    print(f"Most efficient week: {result['weekly_stats']['most_efficient_week']}")
    print(f"Least efficient week: {result['weekly_stats']['least_efficient_week']}")

    # Display the first week of data
    if result['weekly_transitions']:
        print("\n=== First Week Data ===")
        first_week = result['weekly_transitions'][0]
        for key, value in first_week.items():
            if isinstance(value, (int, float)):
                print(f"{key}: {value:.2f}")
            else:
                print(f"{key}: {value}")

    # Display day of week patterns
    if 'actual_minutes' in result['patterns']['day_of_week']:
        print("\n=== Day of Week Patterns (Actual Minutes) ===")
        day_patterns = result['patterns']['day_of_week']['actual_minutes']
        for day, stats in day_patterns['mean'].items():
            print(f"{day}: {stats:.2f} minutes")

    # Display weekly trend for actual minutes
    if 'actual_minutes_mean' in result['patterns']['weekly_trend']:
        trend = result['patterns']['weekly_trend']['actual_minutes_mean']
        print("\n=== Weekly Trend (Actual Minutes) ===")
        print(f"First Week Average: {trend['first_value']:.2f} minutes")
        print(f"Last Week Average: {trend['last_value']:.2f} minutes")
        print(f"Change: {trend['change']:.2f} minutes ({trend['pct_change']:.2f}%)")
        print(f"Trend Direction: {trend['direction']}")

    # Save the results to a file for reference
    output_file = "weekly_transition_analysis.json"
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2, default=str)

    logger.info(f"Results saved to {output_file}")


if __name__ == "__main__":
    asyncio.run(run_example())
