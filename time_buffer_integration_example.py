#!/usr/bin/env python
"""
Integration example for weekly resampling functionality with TimeBufferCalculator.

This example demonstrates how to incorporate the weekly resampling functionality
into the TimeBufferCalculator class for improved buffer time recommendations.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from uuid import UUID, uuid4

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TimeBufferCalculator:
    """
    Enhanced TimeBufferCalculator with weekly transition time pattern analysis.
    
    This class calculates appropriate buffer times between tasks based on
    historical transition data, incorporating weekly pattern analysis.
    """
    
    def __init__(self):
        """Initialize the calculator with default settings."""
        self.logger = logging.getLogger(__name__)
        self.default_buffer_minutes = 15
        self.min_buffer_minutes = 5
        
    async def calculate_buffer(
        self,
        from_task_id: Union[UUID, str],
        to_task_id: Union[UUID, str],
        user_id: Union[UUID, str],
        context_score: float = 1.0,
        task_transition_history: Optional[List[Dict[str, Any]]] = None,
        consider_day_of_week: bool = True,
        consider_weekly_patterns: bool = True
    ) -> Dict[str, Any]:
        """
        Calculate buffer time between tasks using enhanced weekly pattern analysis.
        
        Args:
            from_task_id: ID of the task transitioning from
            to_task_id: ID of the task transitioning to
            user_id: ID of the user
            context_score: Contextual similarity score (0-2, where 1 is neutral)
            task_transition_history: Historical transition data (if None, will be fetched)
            consider_day_of_week: Whether to factor in day-of-week patterns
            consider_weekly_patterns: Whether to use weekly resampling analysis
            
        Returns:
            Dictionary with buffer calculation results
        """
        self.logger.info(f"Calculating buffer time from {from_task_id} to {to_task_id}")
        
        # If no transition history provided, would normally fetch from database
        if task_transition_history is None:
            self.logger.info("No transition history provided, using mock data")
            task_transition_history = self._generate_mock_transition_data(
                user_id=user_id,
                from_task_id=from_task_id,
                to_task_id=to_task_id
            )
        
        # Basic calculation (simplified)
        base_buffer = self._calculate_base_buffer(task_transition_history)
        
        result = {
            "buffer_minutes": base_buffer,
            "explanation": f"Base buffer time between tasks",
            "confidence": 0.7,
            "patterns": {}
        }
        
        # Apply weekly pattern analysis if requested
        if consider_weekly_patterns and task_transition_history:
            weekly_patterns = await self.weekly_resampling(
                transitions=task_transition_history,
                lookback_days=90
            )
            
            # Adjust buffer based on weekly patterns
            buffer_adjustment = self._apply_weekly_pattern_adjustment(
                weekly_patterns=weekly_patterns,
                consider_day_of_week=consider_day_of_week
            )
            
            # Apply adjustment (multiplicative factor)
            adjusted_buffer = max(
                self.min_buffer_minutes,
                int(base_buffer * buffer_adjustment)
            )
            
            result["buffer_minutes"] = adjusted_buffer
            result["weekly_adjustment_factor"] = buffer_adjustment
            result["patterns"] = weekly_patterns
            result["confidence"] = min(0.9, result["confidence"] + 0.2)
            result["explanation"] = f"Buffer time adjusted based on weekly patterns"
        
        # Apply context score adjustment (simplified)
        context_adjustment = 2.0 - context_score  # Higher context score = less buffer needed
        final_buffer = max(
            self.min_buffer_minutes, 
            int(result["buffer_minutes"] * context_adjustment)
        )
        
        result["buffer_minutes"] = final_buffer
        result["context_adjustment_factor"] = context_adjustment
        
        self.logger.info(f"Calculated buffer time: {final_buffer} minutes")
        return result
    
    def _calculate_base_buffer(self, transition_history: List[Dict[str, Any]]) -> int:
        """
        Calculate base buffer time from transition history.
        
        Args:
            transition_history: List of historical transition records
            
        Returns:
            Base buffer time in minutes
        """
        if not transition_history:
            return self.default_buffer_minutes
        
        # Extract actual transition times
        actual_times = [
            record.get("actual_minutes", self.default_buffer_minutes)
            for record in transition_history
            if "actual_minutes" in record
        ]
        
        if not actual_times:
            return self.default_buffer_minutes
        
        # Use 75th percentile for buffer (to account for variability)
        actual_times.sort()
        p75_index = int(len(actual_times) * 0.75)
        p75_value = actual_times[min(p75_index, len(actual_times) - 1)]
        
        # Round to nearest 5 minutes for user-friendly values
        base_buffer = round(p75_value / 5) * 5
        
        return max(self.min_buffer_minutes, base_buffer)
    
    def _apply_weekly_pattern_adjustment(
        self,
        weekly_patterns: Dict[str, Any],
        consider_day_of_week: bool = True
    ) -> float:
        """
        Calculate adjustment factor based on weekly patterns.
        
        Args:
            weekly_patterns: Weekly pattern analysis results
            consider_day_of_week: Whether to factor in day-of-week patterns
            
        Returns:
            Adjustment factor (multiplicative)
        """
        adjustment_factor = 1.0
        
        # Extract day of week patterns if available and requested
        if consider_day_of_week and "patterns" in weekly_patterns:
            day_patterns = weekly_patterns.get("patterns", {}).get("day_of_week", {})
            
            if "actual_minutes" in day_patterns:
                today = datetime.now().strftime("%A")
                day_means = day_patterns["actual_minutes"].get("mean", {})
                
                if today in day_means:
                    today_mean = day_means[today]
                    
                    # Calculate the average of all days
                    all_days_mean = sum(day_means.values()) / len(day_means)
                    
                    if all_days_mean > 0:
                        # If today typically has longer transitions, increase buffer
                        day_factor = today_mean / all_days_mean
                        adjustment_factor *= day_factor
                        logger.info(f"Day-of-week adjustment: {day_factor:.2f}x (Today: {today})")
        
        # Look at trend data to adjust buffer
        if "patterns" in weekly_patterns and "weekly_trend" in weekly_patterns["patterns"]:
            trend_data = weekly_patterns["patterns"]["weekly_trend"]
            
            if "actual_minutes_mean" in trend_data:
                trend_info = trend_data["actual_minutes_mean"]
                
                # If transitions are getting faster (improving), we can reduce buffer slightly
                if trend_info.get("direction") == "improving":
                    pct_change = trend_info.get("pct_change", 0)
                    
                    # Cap the adjustment to prevent extreme changes
                    trend_adjustment = max(0.9, 1.0 - (abs(pct_change) / 100) * 0.2)
                    adjustment_factor *= trend_adjustment
                    logger.info(f"Trend adjustment: {trend_adjustment:.2f}x (Improving trend)")
                
                # If transitions are getting slower (worsening), increase buffer
                elif trend_info.get("direction") == "worsening":
                    pct_change = trend_info.get("pct_change", 0)
                    
                    # Cap the adjustment to prevent extreme changes
                    trend_adjustment = min(1.2, 1.0 + (abs(pct_change) / 100) * 0.3)
                    adjustment_factor *= trend_adjustment
                    logger.info(f"Trend adjustment: {trend_adjustment:.2f}x (Worsening trend)")
        
        # Cap the overall adjustment factor to reasonable bounds
        adjustment_factor = max(0.7, min(1.5, adjustment_factor))
        
        return adjustment_factor
    
    async def weekly_resampling(
        self,
        transitions: List[Dict[str, Any]],
        lookback_days: int = 90,
        rolling_window_days: int = 7,
        include_weekends: bool = True
    ) -> Dict[str, Any]:
        """
        Resample historical task transition data to weekly frequency with rolling averages.
        
        This method implements the same functionality as the standalone WeeklyTaskTransitionAnalyzer
        but integrated directly into the TimeBufferCalculator.
        
        Args:
            transitions: List of transition records with timestamp and metrics
            lookback_days: Number of days to look back for historical data
            rolling_window_days: Size of the rolling window for averages (in days)
            include_weekends: Whether to include weekend data in the analysis
            
        Returns:
            Dictionary containing weekly analysis results
        """
        logger.info("Generating weekly transition time patterns")
        
        # Import pandas and numpy here to keep them optional for basic usage
        try:
            import pandas as pd
            import numpy as np
        except ImportError:
            logger.error("pandas and numpy are required for weekly resampling")
            return {
                "error": "Required libraries not available",
                "weekly_transitions": {},
                "weekly_stats": {},
                "rolling_averages": {},
                "patterns": {}
            }
        
        if not transitions:
            logger.warning("No transition history provided")
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
            # If no timestamp field exists, create one based on current time
            logger.warning("No timestamp field found in transition data, using current date")
            now = datetime.now()
            # Create artificial timestamps spread over the lookback period
            timestamps = [now - timedelta(days=i) for i in range(len(df))]
            df['timestamp'] = timestamps
        
        # Filter to lookback period
        start_date = datetime.now() - timedelta(days=lookback_days)
        df = df[df['timestamp'] >= start_date]
        
        if df.empty:
            logger.warning("No transition data available within lookback period")
            return {
                "error": "No transition data within lookback period",
                "weekly_transitions": {},
                "weekly_stats": {},
                "rolling_averages": {},
                "patterns": {}
            }
        
        # Remove weekend data if specified
        if not include_weekends:
            # 0 = Monday, 6 = Sunday in datetime.weekday()
            df = df[df['timestamp'].dt.weekday < 5]
        
        # Extract numeric variables for analysis
        numeric_cols = []
        for col in df.columns:
            if col in ['actual_minutes', 'predicted_minutes', 'buffer_minutes', 'transition_time']:
                numeric_cols.append(col)
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
            day_data = df[col].groupby(df.index.weekday).agg(['mean', 'std', 'count'])
            day_data.index = day_data.index.map(lambda x: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][x])
            day_patterns[col] = day_data.to_dict()
        
        # Reset index to make timestamp a column again in weekly_df
        weekly_df.reset_index(inplace=True)
        weekly_df.rename(columns={'index': 'week_start'}, inplace=True)
        
        # Prepare result dictionary and safe handling of statistics
        most_efficient_week = None
        least_efficient_week = None
        avg_transitions_per_week = None
        
        if 'actual_minutes_mean' in weekly_df.columns and not weekly_df.empty:
            try:
                min_idx = weekly_df['actual_minutes_mean'].idxmin()
                max_idx = weekly_df['actual_minutes_mean'].idxmax()
                if min_idx is not None and 'week_start' in weekly_df.columns:
                    most_efficient_week = weekly_df.loc[min_idx, 'week_start'].strftime('%Y-%m-%d')
                if max_idx is not None and 'week_start' in weekly_df.columns:
                    least_efficient_week = weekly_df.loc[max_idx, 'week_start'].strftime('%Y-%m-%d')
            except:
                logger.warning("Error calculating most/least efficient weeks")
                
        if 'actual_minutes_count' in weekly_df.columns:
            avg_transitions_per_week = weekly_df['actual_minutes_count'].mean()
        
        result = {
            "weekly_transitions": weekly_df.to_dict(orient='records'),
            "weekly_stats": {
                "total_weeks": len(weekly_df),
                "average_transitions_per_week": avg_transitions_per_week,
                "most_efficient_week": most_efficient_week,
                "least_efficient_week": least_efficient_week,
            },
            "rolling_averages": rolling_weekly.to_dict(orient='records') if not rolling_weekly.empty else {},
            "patterns": {
                "day_of_week": day_patterns,
                "weekly_trend": self._analyze_weekly_trend(weekly_df) if not weekly_df.empty else {}
            }
        }
        
        logger.info("Successfully generated weekly transition patterns")
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
    
    def _generate_mock_transition_data(
        self,
        user_id: Union[UUID, str],
        from_task_id: Union[UUID, str],
        to_task_id: Union[UUID, str],
        num_days: int = 60,
        transitions_per_day: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate mock transition data for demonstration purposes.
        
        In a real implementation, this would be replaced with database queries.
        
        Args:
            user_id: ID of the user
            from_task_id: ID of the source task
            to_task_id: ID of the destination task
            num_days: Number of days of historical data to generate
            transitions_per_day: Average number of transitions per day
            
        Returns:
            List of transition records
        """
        import random
        
        transitions = []
        
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
            day_transitions = max(1, int(transitions_per_day + random.randint(-1, 1)))
            
            # Get weekday (0 = Monday, 6 = Sunday)
            weekday = current_date.weekday()
            weekday_multiplier = weekday_multipliers[weekday]
            
            # Calculate improvement based on how many days have passed
            days_passed = (current_date - start_date).days
            time_improvement = improvement_factor ** days_passed
            
            for _ in range(day_transitions):
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
                    "user_id": str(user_id),
                    "from_task_id": str(from_task_id),
                    "to_task_id": str(to_task_id),
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


async def run_example():
    """Run the integration example."""
    # Generate some task IDs
    from_task_id = str(uuid4())
    to_task_id = str(uuid4())
    user_id = str(uuid4())
    
    # Create the calculator
    calculator = TimeBufferCalculator()
    
    # Run comparisons with and without weekly pattern analysis
    logger.info("Calculating buffer WITHOUT weekly pattern analysis...")
    basic_result = await calculator.calculate_buffer(
        from_task_id=from_task_id,
        to_task_id=to_task_id,
        user_id=user_id,
        consider_weekly_patterns=False
    )
    
    logger.info("Calculating buffer WITH weekly pattern analysis...")
    enhanced_result = await calculator.calculate_buffer(
        from_task_id=from_task_id,
        to_task_id=to_task_id,
        user_id=user_id,
        consider_weekly_patterns=True
    )
    
    # Print the results
    print("\n=== Time Buffer Calculation Results ===")
    print(f"Basic calculation: {basic_result['buffer_minutes']} minutes")
    print(f"Enhanced calculation: {enhanced_result['buffer_minutes']} minutes")
    print(f"Difference: {enhanced_result['buffer_minutes'] - basic_result['buffer_minutes']} minutes")
    
    # Print weekly pattern insights
    if "patterns" in enhanced_result and "weekly_stats" in enhanced_result["patterns"]:
        weekly_stats = enhanced_result["patterns"]["weekly_stats"]
        print("\n=== Weekly Pattern Insights ===")
        print(f"Total weeks analyzed: {weekly_stats['total_weeks']}")
        print(f"Average transitions per week: {weekly_stats['average_transitions_per_week']:.2f}")
        print(f"Most efficient week: {weekly_stats['most_efficient_week']}")
        print(f"Least efficient week: {weekly_stats['least_efficient_week']}")
    
    # Print adjustment factors
    print("\n=== Adjustment Factors ===")
    if "weekly_adjustment_factor" in enhanced_result:
        print(f"Weekly pattern adjustment: {enhanced_result['weekly_adjustment_factor']:.2f}x")
    print(f"Context adjustment: {enhanced_result['context_adjustment_factor']:.2f}x")
    
    # Save the results to a file for reference
    output_file = "time_buffer_integration_example.json"
    with open(output_file, "w") as f:
        # Convert results to a serializable format
        output = {
            "basic_result": basic_result,
            "enhanced_result": {k: v for k, v in enhanced_result.items() if k != "patterns"}
        }
        json.dump(output, f, indent=2, default=str)
    
    logger.info(f"Results saved to {output_file}")


if __name__ == "__main__":
    asyncio.run(run_example()) 