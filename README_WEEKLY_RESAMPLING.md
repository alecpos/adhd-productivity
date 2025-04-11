# Weekly Task Transition Analysis

This module provides functionality to analyze historical task transition data and resample it to weekly frequency, identifying patterns and trends in transition efficiency over time.

## Overview

The weekly resampling feature allows ADHD Calendar users to understand their task transition patterns, helping them:

1. Identify which days of the week have the most efficient/difficult transitions
2. Track improvements in transition times over weeks or months
3. Understand transition time patterns related to different task types
4. Make data-informed decisions about scheduling and task organization

## Key Features

- **Weekly Resampling**: Converts granular transition data into weekly aggregates
- **Rolling Averages**: Calculates smooth rolling averages to visualize trends
- **Day-of-Week Analysis**: Identifies which days have better/worse transition efficiency
- **Trend Detection**: Determines if transition efficiency is improving or worsening over time
- **Comprehensive Statistics**: Provides min, max, average, and standard deviation metrics
- **Data Visualization**: Creates charts and graphs to visualize transition patterns

## Example Output

The weekly resampling analysis produces:

### Weekly Statistics
- Total weeks analyzed
- Average transitions per week
- Most efficient week (lowest average transition time)
- Least efficient week (highest average transition time)

### Day of Week Patterns
Transition times broken down by day of the week, showing which days have better/worse transitions.

### Weekly Trends
Shows whether transition times are improving, worsening, or remaining stable over time.

## Usage

The standalone demo script `weekly_resampling_demo.py` demonstrates how to use this functionality:

```python
# Create an analyzer instance
analyzer = WeeklyTaskTransitionAnalyzer()

# Run the weekly resampling analysis
result = await analyzer.weekly_resampling(
    transitions=transitions_data,  # List of transition records
    lookback_days=90,              # How far back to analyze
    rolling_window_days=7,         # Size of rolling window
    include_weekends=True          # Whether to include weekend data
)

# Access the results
weekly_stats = result['weekly_stats']
day_patterns = result['patterns']['day_of_week']
weekly_trend = result['patterns']['weekly_trend']
```

## Visualization

The `weekly_resampling_visualization.py` script provides visualization capabilities for the analysis results:

```bash
# First run the analysis
python weekly_resampling_demo.py

# Then visualize the results
python weekly_resampling_visualization.py
```

This will generate the following visualizations in the `weekly_transition_analysis_plots` directory:

1. **Weekly Trend Chart**: Shows how transition times change over weeks
2. **Day of Week Chart**: Bar chart showing average transition time by day of week
3. **Heatmap**: Heat map of weekly metrics to identify patterns
4. **Histograms**: Distribution of transition times and prediction errors

These visualizations help identify patterns that might not be obvious from the raw data.

## Integration with the Time Buffer Calculator

This functionality is integrated with the `TimeBufferCalculator` class, which can use the insights from this analysis to provide better buffer time recommendations between tasks based on historical patterns.

## Requirements

- Python 3.8+
- pandas
- numpy
- matplotlib (for visualizations)
- seaborn (for visualizations)

## Future Enhancements

- Advanced visualizations of transition patterns
- ML-based prediction of transition times based on historical patterns
- Integration with calendar optimization algorithms
- Interactive dashboards for real-time monitoring 