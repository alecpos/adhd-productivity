#!/usr/bin/env python
"""
Standalone demo script for weekly resampling of task transition data.

This script demonstrates how to implement and use weekly resampling
functionality for analyzing task transition patterns over time.
"""

import asyncio
import json
import logging
import random
from datetime import datetime, timedelta
from uuid import uuid4

import numpy as np
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class WeeklyTaskTransitionAnalyzer:
    """
    Analyzer for weekly patterns in task transition data.

    This class implements functionality to resample historical task transition data
    to weekly frequency and identify patterns in transition efficiency.
    """

    def __init__(self):
        """Initialize the analyzer."""
        self.logger = logging.getLogger(__name__)

    async def weekly_resampling(
        self, transitions, lookback_days=90, rolling_window_days=7, include_weekends=True
    ):
        """
        Resample historical task transition data to weekly frequency with rolling averages.

        Args:
            transitions: List of transition records with timestamp and metrics
            lookback_days: Number of days to look back for historical data
            rolling_window_days: Size of the rolling window for averages (in days)
            include_weekends: Whether to include weekend data in the analysis

        Returns:
            Dictionary containing:
            - weekly_transitions: Weekly resampled transition data
            - weekly_stats: Statistics for each week
            - rolling_averages: Rolling average transitions
            - patterns: Identified weekly patterns
        """
        self.logger.info("Generating weekly transition time patterns")

        if not transitions:
            self.logger.warning("No transition history provided")
            return {
                "error": "No transition history available",
                "weekly_transitions": {},
                "weekly_stats": {},
                "rolling_averages": {},
                "patterns": {},
            }

        # Convert transitions to DataFrame for analysis
        df = pd.DataFrame(transitions)

        # Ensure timestamp field is in datetime format
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        elif "transition_date" in df.columns:
            df["timestamp"] = pd.to_datetime(df["transition_date"])
        else:
            # If no timestamp field exists, create one based on current time
            self.logger.warning("No timestamp field found in transition data, using current date")
            now = datetime.now()
            # Create artificial timestamps spread over the lookback period
            timestamps = [now - timedelta(days=i) for i in range(len(df))]
            df["timestamp"] = timestamps

        # Filter to lookback period
        start_date = datetime.now() - timedelta(days=lookback_days)
        df = df[df["timestamp"] >= start_date]

        if df.empty:
            self.logger.warning("No transition data available within lookback period")
            return {
                "error": "No transition data within lookback period",
                "weekly_transitions": {},
                "weekly_stats": {},
                "rolling_averages": {},
                "patterns": {},
            }

        # Remove weekend data if specified
        if not include_weekends:
            # 0 = Monday, 6 = Sunday in datetime.weekday()
            df = df[df["timestamp"].dt.weekday < 5]

        # Extract numeric variables for analysis
        numeric_cols = []
        for col in df.columns:
            if col in ["actual_minutes", "predicted_minutes", "buffer_minutes", "transition_time"]:
                numeric_cols.append(col)
            elif df[col].dtype in [np.int64, np.float64]:
                numeric_cols.append(col)

        # Add derived columns for analysis
        if "actual_minutes" in df.columns and "predicted_minutes" in df.columns:
            df["prediction_error"] = df["actual_minutes"] - df["predicted_minutes"]
            df["prediction_error_pct"] = (df["prediction_error"] / df["predicted_minutes"]) * 100
            numeric_cols.extend(["prediction_error", "prediction_error_pct"])

        # Set timestamp as index for resampling
        df.set_index("timestamp", inplace=True)

        # Resample data to weekly frequency
        weekly_aggs = {}
        for col in numeric_cols:
            weekly_aggs[col] = ["mean", "min", "max", "std", "count"]

        weekly_df = df[numeric_cols].resample("W-MON").agg(weekly_aggs)

        # Flatten column MultiIndex
        weekly_df.columns = ["_".join(col).strip() for col in weekly_df.columns.values]

        # Add week number and year
        weekly_df["year"] = weekly_df.index.year
        weekly_df["week_number"] = weekly_df.index.isocalendar().week

        # Calculate rolling averages on daily data first
        daily_df = df[numeric_cols].resample("D").mean()

        # Apply rolling window to the daily data
        rolling_cols = {}
        for col in numeric_cols:
            rolling_col = f"{col}_rolling_{rolling_window_days}d"
            daily_df[rolling_col] = (
                daily_df[col].rolling(window=rolling_window_days, min_periods=1).mean()
            )
            rolling_cols[col] = rolling_col

        # Resample rolling averages to weekly to align with weekly_df
        rolling_weekly = (
            daily_df[[rolling_cols[col] for col in numeric_cols]].resample("W-MON").last()
        )

        # Calculate week-over-week changes
        for col in [c for c in weekly_df.columns if c.endswith("_mean")]:
            weekly_df[f"{col}_wow_change"] = weekly_df[col].pct_change() * 100

        # Identify patterns in day of week variations
        day_patterns = {}
        for col in numeric_cols:
            # Create a DataFrame grouped by day of week
            day_data = df[col].groupby(df.index.weekday).agg(["mean", "std", "count"])
            day_data.index = day_data.index.map(
                lambda x: [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ][x]
            )
            day_patterns[col] = day_data.to_dict()

        # Reset index to make timestamp a column again in weekly_df
        weekly_df.reset_index(inplace=True)
        weekly_df.rename(columns={"index": "week_start"}, inplace=True)

        # Prepare result dictionary and safe handling of statistics
        most_efficient_week = None
        least_efficient_week = None
        avg_transitions_per_week = None

        if "actual_minutes_mean" in weekly_df.columns and not weekly_df.empty:
            try:
                min_idx = weekly_df["actual_minutes_mean"].idxmin()
                max_idx = weekly_df["actual_minutes_mean"].idxmax()
                if min_idx is not None and "week_start" in weekly_df.columns:
                    most_efficient_week = weekly_df.loc[min_idx, "week_start"].strftime("%Y-%m-%d")
                if max_idx is not None and "week_start" in weekly_df.columns:
                    least_efficient_week = weekly_df.loc[max_idx, "week_start"].strftime("%Y-%m-%d")
            except:
                self.logger.warning("Error calculating most/least efficient weeks")

        if "actual_minutes_count" in weekly_df.columns:
            avg_transitions_per_week = weekly_df["actual_minutes_count"].mean()

        result = {
            "weekly_transitions": weekly_df.to_dict(orient="records"),
            "weekly_stats": {
                "total_weeks": len(weekly_df),
                "average_transitions_per_week": avg_transitions_per_week,
                "most_efficient_week": most_efficient_week,
                "least_efficient_week": least_efficient_week,
            },
            "rolling_averages": (
                rolling_weekly.to_dict(orient="records") if not rolling_weekly.empty else {}
            ),
            "patterns": {
                "day_of_week": day_patterns,
                "weekly_trend": (
                    self._analyze_weekly_trend(weekly_df) if not weekly_df.empty else {}
                ),
            },
        }

        self.logger.info("Successfully generated weekly transition patterns")
        return result

    def _analyze_weekly_trend(self, weekly_df):
        """
        Analyze weekly trend to identify patterns over time.

        Args:
            weekly_df: DataFrame with weekly data

        Returns:
            Dictionary with trend analysis
        """
        trend_analysis = {}

        # Find columns that represent means of metrics
        mean_cols = [col for col in weekly_df.columns if col.endswith("_mean")]

        for col in mean_cols:
            if weekly_df[col].count() < 3:  # Need at least 3 data points for meaningful trend
                continue

            # Simple linear trend (is it getting better or worse)
            first_valid = weekly_df[col].first_valid_index()
            last_valid = weekly_df[col].last_valid_index()

            if first_valid is None or last_valid is None:
                continue

            first_value = weekly_df.loc[first_valid, col]
            last_value = weekly_df.loc[last_valid, col]

            # Calculate percentage change
            if abs(first_value) > 0.001:  # Avoid division by very small numbers
                pct_change = ((last_value - first_value) / first_value) * 100
            else:
                pct_change = 0

            trend_analysis[col] = {
                "first_value": first_value,
                "last_value": last_value,
                "change": last_value - first_value,
                "pct_change": pct_change,
                "direction": (
                    "improving" if pct_change < 0 else "worsening" if pct_change > 0 else "stable"
                ),
                "weeks_analyzed": len(weekly_df),
            }

        return trend_analysis


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
        6: 1.1,  # Sunday
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
        time_improvement = improvement_factor**days_passed

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
                "difficulty_level": random.choice(["easy", "moderate", "difficult"]),
            }

            transitions.append(transition)

        # Move to next day
        current_date += timedelta(days=1)

    return transitions


async def run_example():
    """Run the weekly resampling example."""

    # Generate a user ID
    user_id = str(uuid4())

    # Generate sample transition data
    logger.info("Generating sample transition data...")
    transitions = generate_sample_transition_data(user_id, num_days=90, transitions_per_day=5)
    logger.info(f"Generated {len(transitions)} sample transitions")

    # Create an analyzer instance
    analyzer = WeeklyTaskTransitionAnalyzer()

    # Run the weekly resampling analysis
    logger.info("Running weekly resampling analysis...")
    result = await analyzer.weekly_resampling(
        transitions=transitions, lookback_days=90, rolling_window_days=7, include_weekends=True
    )

    # Display the results
    logger.info("Weekly resampling analysis completed")

    # Display summary statistics
    print("\n=== Weekly Transition Time Analysis ===")
    print(f"Total weeks analyzed: {result['weekly_stats']['total_weeks']}")
    print(
        f"Average transitions per week: {result['weekly_stats']['average_transitions_per_week']:.2f}"
    )
    print(f"Most efficient week: {result['weekly_stats']['most_efficient_week']}")
    print(f"Least efficient week: {result['weekly_stats']['least_efficient_week']}")

    # Display the first week of data
    if result["weekly_transitions"]:
        print("\n=== First Week Data ===")
        first_week = result["weekly_transitions"][0]
        for key, value in first_week.items():
            if isinstance(value, (int, float)):
                print(f"{key}: {value:.2f}")
            else:
                print(f"{key}: {value}")

    # Display day of week patterns
    if "actual_minutes" in result["patterns"]["day_of_week"]:
        print("\n=== Day of Week Patterns (Actual Minutes) ===")
        day_patterns = result["patterns"]["day_of_week"]["actual_minutes"]
        for day, stats in day_patterns["mean"].items():
            print(f"{day}: {stats:.2f} minutes")

    # Display weekly trend for actual minutes
    if "actual_minutes_mean" in result["patterns"]["weekly_trend"]:
        trend = result["patterns"]["weekly_trend"]["actual_minutes_mean"]
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
