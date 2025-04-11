# Task Transition Time Analysis Guide

This guide provides a comprehensive overview of the task transition time analysis capabilities in the ADHD Calendar application, focusing on the weekly resampling functionality for improved task scheduling.

## Overview

Task transition time analysis helps users understand patterns in how long it takes to switch between different tasks. By analyzing historical transition data, the system can:

1. Identify patterns in transition efficiency across different days of the week
2. Track improvement or decline in transition times over weeks and months
3. Make data-driven recommendations for buffer times between scheduled tasks
4. Help users make better scheduling decisions based on personal transition patterns

## Components

The implementation consists of several complementary components:

### 1. Weekly Task Transition Analyzer

The standalone `WeeklyTaskTransitionAnalyzer` class provides core functionality for analyzing transition patterns. It processes historical transition data and generates weekly aggregates, identifies day-of-week patterns, and detects trends over time.

```python
# Example usage
analyzer = WeeklyTaskTransitionAnalyzer()
result = await analyzer.weekly_resampling(
    transitions=transitions_data,
    lookback_days=90,
    rolling_window_days=7,
    include_weekends=True
)
```

### 2. TimeBufferCalculator Integration

The `TimeBufferCalculator` class has been enhanced with weekly resampling capabilities to provide more accurate buffer time recommendations between tasks. It analyzes past transition data to adjust buffer times based on:

- Day of week patterns (e.g., longer transitions on Mondays)
- Weekly trends (e.g., improving transition efficiency over time)
- Context similarity between tasks

```python
# Example usage
calculator = TimeBufferCalculator()
buffer_result = await calculator.calculate_buffer(
    from_task_id="task1",
    to_task_id="task2",
    user_id="user1",
    context_score=1.0,
    consider_weekly_patterns=True
)
```

### 3. Data Visualization

The visualization component creates charts and graphs to help users understand their transition patterns visually:

- Weekly trend charts showing how transition times change over weeks
- Day-of-week bar charts highlighting which days have better/worse transitions
- Heatmaps for identifying patterns across weeks
- Histograms showing the distribution of transition times

## Data Structure

Transition records should include the following fields:

```json
{
  "user_id": "user-uuid",
  "from_task_id": "task-uuid-1",
  "to_task_id": "task-uuid-2",
  "actual_minutes": 15,           // Actual transition time
  "predicted_minutes": 12,         // Predicted transition time (if available)
  "timestamp": "2025-03-15T14:30:00",  // When the transition occurred
  "context_score": 0.8,           // Similarity between tasks (optional)
  "difficulty_level": "moderate"  // Subjective difficulty (optional)
}
```

## Analysis Results

The weekly resampling analysis produces a comprehensive result object with the following sections:

### Weekly Transitions

A list of weekly aggregated data points containing:
- Timestamp for the week
- Mean, min, max, std, and count of transition times
- Week-over-week percentage changes
- Year and week number

### Weekly Statistics

Summary statistics about the analyzed period:
- Total weeks analyzed
- Average transitions per week
- Most efficient week (lowest average transition time)
- Least efficient week (highest average transition time)

### Day of Week Patterns

Transition times broken down by day of the week, showing which days have better/worse transitions:
```
Monday: 14.12 minutes
Tuesday: 12.31 minutes
Wednesday: 10.80 minutes
Thursday: 9.81 minutes
Friday: 8.64 minutes
Saturday: 13.81 minutes
Sunday: 12.00 minutes
```

### Weekly Trends

Analysis of whether transition times are improving, worsening, or remaining stable over time:
```
First Week Average: 15.06 minutes
Last Week Average: 8.62 minutes
Change: -6.44 minutes (-42.79%)
Trend Direction: improving
```

## Buffer Time Calculation

The enhanced `TimeBufferCalculator` uses the weekly pattern analysis to provide more accurate buffer time recommendations:

1. Calculate base buffer time from historical transition data
2. Apply adjustments based on weekly patterns:
   - Day-of-week adjustment based on the current day's typical performance
   - Trend adjustment based on overall improvement or decline
3. Apply context adjustment based on the similarity between tasks

The result is a more personalized buffer time recommendation that accounts for the user's unique transition patterns.

## Practical Example

Consider a user who consistently has longer transition times on Mondays (30% longer than average) and has been showing improvement in transition efficiency over time (42% reduction over 3 months).

When scheduling a transition on Monday, the system might recommend:
- Base buffer: 15 minutes
- Monday adjustment: +30% (factor of 1.3)
- Improvement trend: -10% (factor of 0.9)
- Final adjustment: 1.3 × 0.9 = 1.17
- Recommended buffer: 15 × 1.17 = 18 minutes

But for a Friday transition:
- Base buffer: 15 minutes
- Friday adjustment: -20% (factor of 0.8)
- Improvement trend: -10% (factor of 0.9)
- Final adjustment: 0.8 × 0.9 = 0.72
- Recommended buffer: 15 × 0.72 = 11 minutes

## Integration Steps

To integrate the weekly resampling functionality into an existing application:

1. **Data Collection**: Ensure you're collecting transition time data with timestamps
2. **Analysis**: Implement the `weekly_resampling` method to analyze historical data
3. **Visualization**: Use the visualization tools to help users understand their patterns
4. **Buffer Calculation**: Enhance buffer time recommendations using the weekly patterns
5. **User Experience**: Present the insights to users in a way that helps them make better scheduling decisions

## Requirements

- Python 3.8+
- pandas
- numpy
- matplotlib (for visualizations)
- seaborn (for visualizations)

## Demo Files

The repository includes several demo files to help you understand and implement the functionality:

- `weekly_resampling_demo.py`: Standalone demo of the weekly resampling analyzer
- `weekly_resampling_visualization.py`: Visualization tools for the analysis results
- `time_buffer_integration_example.py`: Example of integrating with buffer calculation
- `README_WEEKLY_RESAMPLING.md`: Documentation for the weekly resampling feature

## Future Enhancements

- ML-based prediction of transition times based on historical patterns
- Integration with calendar optimization algorithms
- Interactive dashboards for real-time monitoring
- Personalized recommendations for scheduling based on transition patterns
- Mobile notifications to help prepare for difficult transitions
