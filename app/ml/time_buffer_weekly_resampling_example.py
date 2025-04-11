#!/usr/bin/env python3

"""
Weekly Resampling Example Script for TimeBufferCalculator

This script demonstrates the weekly_resampling method of the TimeBufferCalculator class,
which analyzes task transition data over time and resamples it to a weekly frequency for
pattern identification and trend analysis.
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Any, Optional

# Define custom JSON encoder for pandas types
class PandasJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for pandas and numpy objects."""
    def default(self, obj):
        if isinstance(obj, (pd.Timestamp, pd._libs.tslibs.timestamps.Timestamp)):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif pd.isna(obj):
            return None
        return super().default(obj)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define transition difficulty enum for sample data
class TransitionDifficulty(Enum):
    EASY = "easy"
    MODERATE = "moderate"
    DIFFICULT = "difficult"
    VERY_DIFFICULT = "very_difficult"

class TimeBufferCalculatorDemo:
    """Demo version of TimeBufferCalculator with weekly_resampling functionality."""

    def __init__(self):
        self.lookback_period = 90  # Default lookback period in days

    async def weekly_resampling(
        self,
        user_id: str,
        lookback_days: int = 90,
        rolling_window_days: int = 7,
        include_weekends: bool = True
    ) -> Dict[str, Any]:
        """
        Resample historical task transition data to weekly frequency with rolling averages.

        This method analyzes historical transition times between tasks and resamples the data
        to weekly frequency, calculating rolling averages and other useful statistics to identify
        patterns in task switching efficiency over time.

        Args:
            user_id: ID of the user whose data will be analyzed
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
        logger.info(f"Generating weekly transition time patterns for user {user_id}")

        # Get transition history
        transitions = await self._get_transition_history(user_id, lookback_days)

        if not transitions:
            logger.warning(f"No transition history found for user {user_id}")
            return {
                "error": "No transition history available",
                "weekly_transitions": {},
                "weekly_stats": {},
                "rolling_averages": {},
                "patterns": {}
            }

        # Convert transitions to DataFrame for analysis
        df = pd.DataFrame(transitions)

        # Ensure timestamp field is in datetime format
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        elif 'transition_date' in df.columns:
            df['timestamp'] = pd.to_datetime(df['transition_date'])
        else:
            logger.error("No timestamp column found in transition data")
            return {
                "error": "Missing timestamp data",
                "weekly_transitions": {},
                "weekly_stats": {},
                "rolling_averages": {},
                "patterns": {}
            }

        # Filter out weekends if specified
        if not include_weekends:
            weekday_mask = (df['timestamp'].dt.dayofweek < 5)  # 0-4 are Monday to Friday
            df = df[weekday_mask]
            if df.empty:
                logger.warning("No weekday data available after filtering")
                return {
                    "error": "No weekday data available",
                    "weekly_transitions": {},
                    "weekly_stats": {},
                    "rolling_averages": {},
                    "patterns": {}
                }

        # Find numeric columns for aggregation
        numeric_cols = []
        for col in df.columns:
            if col in ['timestamp', 'user_id', 'current_task_id', 'next_task_id', 'category_keys']:
                continue
            elif df[col].dtype in [np.int64, np.float64]:
                numeric_cols.append(col)

        # Add derived columns for analysis
        if 'actual_minutes' in df.columns and 'predicted_minutes' in df.columns:
            df['prediction_error'] = df['actual_minutes'] - df['predicted_minutes']
            df['prediction_error_pct'] = (df['prediction_error'] / df['predicted_minutes']) * 100
            numeric_cols.extend(['prediction_error', 'prediction_error_pct'])

        # Set timestamp as index for resampling
        df.set_index('timestamp', inplace=True)

        # Resample data to weekly frequency
        weekly_aggs = {}
        for col in numeric_cols:
            weekly_aggs[col] = ['mean', 'min', 'max', 'std', 'count']

        weekly_df = df[numeric_cols].resample('W-MON').agg(weekly_aggs)

        # Flatten column MultiIndex
        weekly_df.columns = ['_'.join(col).strip() for col in weekly_df.columns.values]

        # Add week number and year
        weekly_df['year'] = weekly_df.index.year
        weekly_df['week_number'] = weekly_df.index.isocalendar().week

        # Calculate rolling averages on daily data first
        daily_df = df[numeric_cols].resample('D').mean()

        # Apply rolling window to the daily data
        rolling_cols = {}
        for col in numeric_cols:
            rolling_col = f"{col}_rolling_{rolling_window_days}d"
            daily_df[rolling_col] = daily_df[col].rolling(window=rolling_window_days, min_periods=1).mean()
            rolling_cols[col] = rolling_col

        # Resample rolling averages to weekly to align with weekly_df
        rolling_weekly = daily_df[[rolling_cols[col] for col in numeric_cols]].resample('W-MON').last()

        # Calculate week-over-week changes
        for col in [c for c in weekly_df.columns if c.endswith('_mean')]:
            weekly_df[f'{col}_wow_change'] = weekly_df[col].pct_change() * 100

        # Identify patterns in day of week variations
        day_patterns = {}
        for col in numeric_cols:
            # Create a DataFrame grouped by day of week
            day_data = df[col].groupby(df.index.dayofweek).agg(['mean', 'std', 'count'])
            day_data.index = day_data.index.map(lambda x: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][x])
            day_patterns[col] = day_data.to_dict()

        # Reset index to make timestamp a column again in weekly_df
        weekly_df.reset_index(inplace=True)
        weekly_df.rename(columns={'index': 'week_start'}, inplace=True)

        # Convert rolling weekly to a JSON-safe format
        rolling_weekly_safe = []
        if not rolling_weekly.empty:
            # Reset index to make timestamp a column
            rolling_weekly.reset_index(inplace=True)
            rolling_weekly.rename(columns={'index': 'date'}, inplace=True)
            rolling_weekly_safe = rolling_weekly.to_dict(orient='records')

        # Prepare result dictionary
        result = {
            "weekly_transitions": weekly_df.to_dict(orient='records'),
            "weekly_stats": {
                "total_weeks": len(weekly_df),
                "average_transitions_per_week": weekly_df['actual_minutes_count'].mean() if 'actual_minutes_count' in weekly_df.columns else None,
                "most_efficient_week": None,
                "least_efficient_week": None,
            },
            "rolling_averages": rolling_weekly_safe,
            "patterns": {
                "day_of_week": day_patterns,
                "weekly_trend": self._analyze_weekly_trend(weekly_df) if not weekly_df.empty else {}
            }
        }

        # Add most/least efficient week if we have the required columns
        if 'actual_minutes_mean' in weekly_df.columns and 'week_start' in weekly_df.columns and not weekly_df.empty:
            try:
                min_idx = weekly_df['actual_minutes_mean'].idxmin()
                max_idx = weekly_df['actual_minutes_mean'].idxmax()

                if pd.notnull(min_idx) and pd.notnull(max_idx):
                    result["weekly_stats"]["most_efficient_week"] = weekly_df.loc[min_idx, 'week_start'].strftime('%Y-%m-%d') if isinstance(weekly_df.loc[min_idx, 'week_start'], datetime) else str(weekly_df.loc[min_idx, 'week_start'])
                    result["weekly_stats"]["least_efficient_week"] = weekly_df.loc[max_idx, 'week_start'].strftime('%Y-%m-%d') if isinstance(weekly_df.loc[max_idx, 'week_start'], datetime) else str(weekly_df.loc[max_idx, 'week_start'])
            except Exception as e:
                logger.warning(f"Could not determine most/least efficient weeks: {e}")

        logger.info(f"Successfully generated weekly transition patterns for user {user_id}")
        return result

    def _analyze_weekly_trend(self, weekly_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze weekly trend to identify patterns over time.

        Args:
            weekly_df: DataFrame with weekly data

        Returns:
            Dictionary with trend analysis
        """
        trend_analysis = {}

        # Find columns that represent means of metrics
        mean_cols = [col for col in weekly_df.columns if col.endswith('_mean')]

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
                "direction": "improving" if pct_change < 0 else "worsening" if pct_change > 0 else "stable",
                "weeks_analyzed": len(weekly_df)
            }

        return trend_analysis

    async def _get_transition_history(self, user_id: str, days: int = 90) -> List[Dict[str, Any]]:
        """
        Generate mock transition history for a user.

        Args:
            user_id: ID of the user
            days: Number of days of history to generate

        Returns:
            List of transition records
        """
        # Generate mock data for demonstration
        transitions = []

        # Generate data for the specified number of days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Use a seed for reproducible random data
        np.random.seed(42)

        # Create transitions spread over the date range
        current_date = start_date
        while current_date < end_date:
            # Generate more transitions on weekdays
            is_weekday = current_date.weekday() < 5
            daily_transitions = np.random.randint(2, 10) if is_weekday else np.random.randint(0, 4)

            for _ in range(daily_transitions):
                hour = np.random.randint(8, 20)  # Between 8 AM and 8 PM
                timestamp = current_date.replace(hour=hour, minute=np.random.randint(0, 60))

                # Random task IDs
                current_task_id = f"task{np.random.randint(1, 10)}"
                next_task_id = f"task{np.random.randint(1, 10)}"

                # Simulate task difficulty pattern - tasks are harder earlier in the week
                day_factor = 1.0 - (current_date.weekday() / 10)  # Higher factor on Monday

                # Add time of day pattern - transitions take longer in the afternoon
                hour_factor = 1.0 + (0.5 * (hour - 8) / 12)  # Higher factor later in the day

                # Calculate transition time with patterns
                predicted_minutes = np.random.randint(5, 25)
                base_actual = np.random.normal(predicted_minutes, predicted_minutes * 0.3)
                actual_minutes = max(1, int(base_actual * day_factor * hour_factor))

                # More difficult transitions later in the day
                difficulty_options = list(TransitionDifficulty)
                difficulty_weights = [
                    0.4 - (hour / 50),  # EASY: less likely later in the day
                    0.4,                 # MODERATE: consistent
                    0.1 + (hour / 40),   # DIFFICULT: more likely later
                    0.1 * hour_factor    # VERY_DIFFICULT: more likely later
                ]
                # Normalize weights
                difficulty_weights = [max(0.01, w) for w in difficulty_weights]
                difficulty_weights = [w / sum(difficulty_weights) for w in difficulty_weights]

                difficulty = np.random.choice(difficulty_options, p=difficulty_weights)

                # Generate category keys based on tasks
                category_keys = []
                if int(current_task_id[4:]) <= 3 and int(next_task_id[4:]) <= 3:
                    category_keys.append("cat:work->work")
                elif int(current_task_id[4:]) <= 3 and int(next_task_id[4:]) > 3:
                    category_keys.append("cat:work->personal")
                elif int(current_task_id[4:]) > 3 and int(next_task_id[4:]) <= 3:
                    category_keys.append("cat:personal->work")
                else:
                    category_keys.append("cat:personal->personal")

                # Add difficulty to category keys
                category_keys.append(f"diff:{difficulty.value}")

                # Add time of day
                if hour < 12:
                    category_keys.append("time:morning")
                elif hour < 17:
                    category_keys.append("time:afternoon")
                else:
                    category_keys.append("time:evening")

                transitions.append({
                    "user_id": user_id,
                    "current_task_id": current_task_id,
                    "next_task_id": next_task_id,
                    "predicted_minutes": predicted_minutes,
                    "actual_minutes": actual_minutes,
                    "transition_difficulty": difficulty.value,
                    "category_keys": category_keys,
                    "timestamp": timestamp.isoformat()
                })

            # Move to next day
            current_date += timedelta(days=1)

        return transitions

def plot_weekly_patterns(result):
    """Plot key insights from the weekly resampling analysis."""
    try:
        # Extract weekly transitions data
        weekly_transitions = pd.DataFrame(result["weekly_transitions"])

        if weekly_transitions.empty:
            logger.error("Cannot generate plots: No weekly transition data available")
            return

        # Determine date column (could be either 'week_start' or 'timestamp')
        date_column = None
        if 'week_start' in weekly_transitions.columns:
            date_column = 'week_start'
        elif 'timestamp' in weekly_transitions.columns:
            date_column = 'timestamp'
        else:
            logger.error("Cannot generate plots: No date column (week_start or timestamp) found in data")
            return

        # Convert date column to datetime if it's not already
        weekly_transitions[date_column] = pd.to_datetime(weekly_transitions[date_column])

        # Create the figure
        plt.figure(figsize=(12, 8))

        # Plot actual vs predicted transition times
        if 'actual_minutes_mean' in weekly_transitions.columns and 'predicted_minutes_mean' in weekly_transitions.columns:
            plt.subplot(2, 2, 1)
            plt.plot(weekly_transitions[date_column], weekly_transitions['actual_minutes_mean'], 'b-', label='Actual')
            plt.plot(weekly_transitions[date_column], weekly_transitions['predicted_minutes_mean'], 'g--', label='Predicted')
            plt.xlabel('Week')
            plt.ylabel('Minutes')
            plt.title('Weekly Average Transition Times')
            plt.legend()
            plt.xticks(rotation=45)
            plt.tight_layout()

        # Plot prediction error
        if 'prediction_error_mean' in weekly_transitions.columns:
            plt.subplot(2, 2, 2)
            plt.plot(weekly_transitions[date_column], weekly_transitions['prediction_error_mean'], 'r-')
            plt.xlabel('Week')
            plt.ylabel('Error (minutes)')
            plt.title('Weekly Average Prediction Error')
            plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
            plt.xticks(rotation=45)
            plt.tight_layout()

        # Plot day of week patterns if available
        if 'actual_minutes' in result["patterns"]["day_of_week"]:
            day_data = result["patterns"]["day_of_week"]["actual_minutes"]
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

            plt.subplot(2, 2, 3)
            means = [day_data['mean'].get(day, 0) for day in days]
            plt.bar(days, means)
            plt.xlabel('Day of Week')
            plt.ylabel('Average Minutes')
            plt.title('Transition Time by Day of Week')
            plt.xticks(rotation=45)
            plt.tight_layout()

        # Plot weekly trend
        if result["patterns"]["weekly_trend"] and "actual_minutes_mean" in result["patterns"]["weekly_trend"]:
            trend = result["patterns"]["weekly_trend"]["actual_minutes_mean"]

            plt.subplot(2, 2, 4)
            plt.text(0.5, 0.5, f"Trend Direction: {trend['direction']}\n" +
                              f"First Value: {trend['first_value']:.2f}\n" +
                              f"Last Value: {trend['last_value']:.2f}\n" +
                              f"Change: {trend['change']:.2f}\n" +
                              f"% Change: {trend['pct_change']:.2f}%",
                     horizontalalignment='center',
                     verticalalignment='center',
                     transform=plt.gca().transAxes,
                     fontsize=12)
            plt.axis('off')
            plt.title('Transition Time Trend Analysis')

        plt.tight_layout()
        plt.savefig('weekly_transition_analysis.png')
        logger.info("Analysis plots saved to weekly_transition_analysis.png")

    except Exception as e:
        logger.error(f"Error plotting results: {e}")
        import traceback
        logger.error(traceback.format_exc())

async def main():
    # Create calculator demo instance
    calculator = TimeBufferCalculatorDemo()

    # Run weekly resampling analysis
    user_id = "demo_user_123"
    result = await calculator.weekly_resampling(
        user_id=user_id,
        lookback_days=90,
        rolling_window_days=7,
        include_weekends=True
    )

    # Save results to file
    with open('weekly_resampling_result.json', 'w') as f:
        json.dump(result, f, indent=2, cls=PandasJSONEncoder)

    logger.info("Weekly resampling results saved to weekly_resampling_result.json")

    # Generate visualizations
    plot_weekly_patterns(result)

    # Print key statistics
    print("\n=== WEEKLY TRANSITION TIME ANALYSIS ===")
    print(f"Total weeks analyzed: {result['weekly_stats']['total_weeks']}")
    print(f"Avg. transitions per week: {result['weekly_stats']['average_transitions_per_week']:.2f}")

    if result['weekly_stats']['most_efficient_week']:
        print(f"Most efficient week: {result['weekly_stats']['most_efficient_week']}")

    if result['weekly_stats']['least_efficient_week']:
        print(f"Least efficient week: {result['weekly_stats']['least_efficient_week']}")

    # Print day of week patterns
    if 'actual_minutes' in result["patterns"]["day_of_week"]:
        print("\nTransition Times by Day of Week:")
        day_data = result["patterns"]["day_of_week"]["actual_minutes"]["mean"]
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            if day in day_data:
                print(f"  {day}: {day_data[day]:.2f} minutes")

if __name__ == "__main__":
    asyncio.run(main())
