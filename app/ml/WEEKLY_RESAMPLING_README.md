# Weekly Resampling Analysis for Task Transitions

This directory contains functionality for analyzing task transition times using weekly resampling techniques. This README explains the purpose of the analysis, how to use it, and what insights can be gained.

## Overview

The weekly resampling analysis helps identify patterns in task transition times over different time periods, such as:

- Differences in transition times by day of the week
- Weekly trends over time (improving or worsening)
- Time-of-day patterns
- Prediction accuracy over time

This analysis is particularly valuable for users with ADHD who may struggle with task transitions and can benefit from understanding their personal patterns.

## Implementation

The core functionality is implemented in `TimeBufferCalculator` class's `weekly_resampling` method. This method:

1. Collects historical task transition data for a user
2. Resamples the time series data to weekly frequency
3. Calculates rolling averages and statistical measures
4. Identifies patterns across days and weeks
5. Returns structured analysis results as a JSON object

## Example Scripts

### time_buffer_weekly_resampling_example.py

This script demonstrates a standalone implementation of the weekly resampling functionality. It includes:

- Mock data generation with realistic patterns (more transitions on weekdays, varying difficulties by time of day)
- Implementation of the weekly_resampling algorithm
- Visualization of results with matplotlib
- JSON export of analysis results

To run the example:

```bash
python app/ml/time_buffer_weekly_resampling_example.py
```

This will:
1. Generate sample transition data
2. Run the weekly resampling analysis
3. Save the results to `weekly_resampling_result.json`
4. Create visualizations in `weekly_transition_analysis.png`
5. Print key statistics to the console

## Analysis Outputs

The weekly resampling analysis produces the following insights:

- **Weekly Transitions**: Statistics for each week, including mean, min, max, and standard deviation of transition times
- **Weekly Stats**: Summary statistics about the entire dataset
- **Rolling Averages**: Rolling window averages to smooth out variability
- **Patterns**:
  - **Day of Week**: How transition times vary by day of the week
  - **Weekly Trend**: Whether transition times are improving, worsening, or stable over time

## Integration with ADHD Calendar Backend

This functionality can be integrated with the calendar and task systems to:

1. Provide users with insights about their task transition patterns
2. Make more accurate time buffer predictions based on historical trends
3. Schedule tasks more effectively by accounting for transition time patterns
4. Suggest optimal task ordering based on transition efficiency

## Dependencies

The weekly resampling functionality requires:
- pandas
- numpy
- datetime

For visualization:
- matplotlib

## Future Enhancements

Potential enhancements to the weekly resampling functionality:

1. Add seasonal analysis (monthly, quarterly patterns)
2. Implement anomaly detection for unusually difficult transitions
3. Provide personalized recommendations based on discovered patterns
4. Integrate with machine learning models for predictive analytics 