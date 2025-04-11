# Epic 2: User Guide - Stochastic Time Estimation Engine

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Understanding Time Estimates](#understanding-time-estimates)
4. [Task Complexity Analysis](#task-complexity-analysis)
5. [Managing Stressors](#managing-stressors)
6. [Using Time Buffers](#using-time-buffers)
7. [Integration with Calendar](#integration-with-calendar)
8. [Mobile Experience](#mobile-experience)
9. [Troubleshooting](#troubleshooting)
10. [Tips and Best Practices](#tips-and-best-practices)
11. [FAQ](#faq)

## Introduction

The Stochastic Time Estimation Engine is designed specifically for individuals with ADHD to overcome the challenge of time blindness and unrealistic time estimation. This guide will help you understand and make the most of its features.

### Key Benefits

- **Realistic Time Estimates**: Get personalized duration predictions based on your actual patterns, not idealized scenarios
- **Confidence Intervals**: Understand the range of possible durations, not just a single number
- **Task Complexity Analysis**: Automatically identify complex or ambiguous tasks that might take longer
- **Environmental Awareness**: Account for factors like noise, interruptions, and physiological state
- **Smart Buffers**: Add appropriate transition time between tasks
- **Continuous Learning**: The system improves as it learns your patterns

### How It's Different

Traditional calendars and task managers force you to specify exact durations without context. Our Stochastic Time Estimation Engine:

- Acknowledges the variability in how long tasks actually take
- Considers your personal ADHD profile and current context
- Provides probabilities rather than false certainty
- Adapts to your actual performance over time

![Time Estimation Overview](../assets/images/time_estimation_overview.png)

## Getting Started

### Setting Up Your Profile

Before you begin using the time estimation features, take a few minutes to set up your ADHD profile:

1. Navigate to **Settings → Personal Profile**
2. Complete the **ADHD Characteristics** questionnaire
3. Connect any wearable devices (optional but recommended)
4. Review and adjust your **Working Hours** preferences
5. Set up **Environment Sensors** if available

### Initial Calibration Period

The system needs data to provide accurate estimates. During the first two weeks:

- Create tasks with your best-guess durations
- Record actual completion times
- Note any factors that affected your focus
- Complete the brief end-of-day reflections when prompted

This initial data helps the system understand your patterns and provide more accurate estimates going forward.

## Understanding Time Estimates

### Reading Time Predictions

When you create a task, the system provides a time estimate with three important values:

![Time Estimate Explanation](../assets/images/time_estimate_explanation.png)

1. **Expected Duration**: The most likely time needed (50th percentile)
2. **Minimum Duration**: Shorter duration possible with optimal conditions (10th percentile)
3. **Maximum Duration**: Longer duration accounting for challenges (90th percentile)

### Confidence Indicators

Each estimate includes a visual confidence indicator:

- **High Confidence** 🟢: System has substantial data for this type of task
- **Medium Confidence** 🟠: System has some relevant data
- **Low Confidence** 🔴: System has limited data for this scenario

### Factors Influencing Estimates

Tap "View Factors" to see what's influencing your time estimate:

- **Historical Data**: How long similar tasks have taken you
- **Task Complexity**: Analysis of the task description
- **Current Context**: Time of day, energy level, potential stressors
- **Similar User Patterns**: Anonymous data from users with similar ADHD profiles

### Improving Estimates

The more you use the system, the better it gets. To improve estimates:

1. Always mark tasks as complete when finished
2. Periodically review your time estimation accuracy in the Insights section
3. Check in your current state when prompted throughout the day
4. Complete the optional context questionnaires

## Task Complexity Analysis

### Understanding Complexity Scores

The system automatically analyzes task descriptions to evaluate complexity:

![Complexity Analysis](../assets/images/complexity_analysis.png)

- **Overall Complexity** (0-100): Combined assessment of difficulty
- **Cognitive Load** (0-10): Mental effort required
- **Ambiguity Index** (0-10): How clear or vague the task is
- **Subtask Estimate**: Number of implicit smaller tasks detected

### Improving Task Descriptions

To get better estimates and reduce ambiguity:

- Be specific about deliverables
- Break down vague tasks into clearer steps
- Include relevant details like "draft" vs "final"
- Use consistent terminology for recurring tasks

**Example Improvements:**

| Vague Description | Improved Description |
|-------------------|----------------------|
| "Write report" | "Write first draft of Q3 sales report (5 pages)" |
| "Meeting prep" | "Prepare 3 slides for client project kickoff meeting" |
| "Email people" | "Respond to 5 priority customer support emails" |

### Task Templates

For recurring tasks, use templates to maintain consistency:

1. Find a completed task with an accurate time estimate
2. Select "Save as Template" from the task menu
3. Give the template a clear name
4. Access templates from the "New Task" menu

## Managing Stressors

### Stressor Detection

The system can detect factors that may impact your focus and productivity:

![Stressor Detection](../assets/images/stressor_detection.png)

- **Environmental**: Noise levels, interruptions, temperature
- **Physiological**: Sleep quality, hunger, medication timing
- **Cognitive**: Task switching frequency, mental fatigue
- **Social**: Meeting load, collaboration requirements

### Manual Stressor Tracking

For more accurate estimates, manually log stressors:

1. Tap the "Current State" button in the dashboard
2. Select any active stressors from the list
3. Rate their intensity (1-10)
4. Optionally add notes about their impact

### Stressor Insights

Review your stressor patterns to improve productivity:

1. Navigate to **Insights → Stressor Impact**
2. View your most frequent and impactful stressors
3. See how different stressors affect different task types
4. Review recommendations for stressor management

### Environment Optimization

Based on stressor data, the system provides recommendations:

- Best times of day for focused work
- Ideal environments for different task types
- Recovery activities between challenging tasks
- Environmental adjustments (lighting, noise, etc.)

## Using Time Buffers

### Buffer Recommendation

The system automatically suggests buffer time between tasks:

![Buffer Recommendation](../assets/images/buffer_recommendation.png)

- **Transition Difficulty**: Rating of the cognitive shift required
- **Recovery Time**: Recommended break based on previous task intensity
- **Context Switch Cost**: Time needed to refocus on the new task
- **Preparation Needs**: Time for gathering materials or mental preparation

### Customizing Buffers

While automated buffers are recommended, you can adjust them:

1. Tap on a buffer in your schedule
2. Drag to increase or decrease duration
3. Set custom buffer activities
4. Save preferences for similar transitions

### Buffer Activities

Make the most of buffer time with suggested activities:

- **1-5 minute buffers**: Quick stretches, water break, deep breathing
- **5-15 minute buffers**: Brief walk, meditation, simple task completion
- **15+ minute buffers**: Light exercise, meal, nature exposure, power nap

### Buffer Settings

Customize your buffer preferences in Settings:

1. Navigate to **Settings → Time Buffers**
2. Set minimum and maximum buffer times
3. Configure transition types that need longer buffers
4. Customize buffer visualization in your calendar

## Integration with Calendar

### Calendar View Options

The system integrates with your existing calendar with special views:

![Calendar Integration](../assets/images/calendar_integration.png)

- **Reality Mode**: Shows realistic durations with buffers
- **Optimistic Mode**: Shows minimum durations (useful for possibility planning)
- **Traditional View**: Standard calendar view without probabilistic features
- **Focus Mode**: Highlights only the current and next tasks

### Schedule Optimization

Let the system help optimize your day:

1. Go to **Schedule → Optimize Day**
2. Select tasks you need to complete
3. Specify any fixed appointments or commitments
4. Choose optimization priority (energy, focus, completion probability)
5. Review and adjust the suggested schedule

### Handling Schedule Conflicts

When time estimates create conflicts:

1. The system highlights the conflict area in your calendar
2. Tap "Resolve Conflict" to see options:
   - Reschedule less time-sensitive tasks
   - Adjust buffer times
   - Split tasks into smaller segments
   - Delegate or defer tasks

### Calendar Notifications

Customize notifications to stay on track:

- **Buffer Start**: Notification when it's time to wrap up current task
- **Next Task Preview**: Advance notice of upcoming tasks
- **Duration Alerts**: Notifications when approaching estimated maximum time
- **Context Shifts**: Reminders when entering a new environment

## Mobile Experience

### Mobile App Features

The mobile app provides on-the-go time management:

![Mobile Experience](../assets/images/mobile_experience.png)

- Real-time stressor detection using phone sensors
- Voice input for quick task creation
- Location-aware scheduling suggestions
- Wearable device integration for physiological data

### Voice Commands

Use voice commands for hands-free operation:

- "Create new task: [description]"
- "How long will it take to [task description]?"
- "Add a buffer after my next meeting"
- "Log stressor: noisy environment"

### Wearable Integration

Connect your wearable device for enhanced features:

1. Go to **Settings → Connected Devices**
2. Select your device from the list
3. Authorize the requested permissions
4. Choose which metrics to track (heart rate, HRV, sleep data, etc.)

## Troubleshooting

### Common Issues and Solutions

| Issue | Possible Cause | Solution |
|-------|---------------|----------|
| Estimates seem too long | Initial calibration phase | Continue logging actual durations for 2-3 weeks |
| Consistently finishing early | Productivity improvement or overly cautious estimates | Check insights for trends and adjust in settings |
| Estimates vary too widely | Insufficient data or highly variable performance | Add more context details and ensure consistent task descriptions |
| Stressors not detected | Missing wearable data or permissions | Check device connections and permissions |
| Calendar conflicts | Overlapping estimates or insufficient buffers | Use the conflict resolution tool or adjust buffer settings |

### Feedback System

Help improve the system by providing feedback:

1. Tap the feedback icon on any estimate or recommendation
2. Rate the accuracy from 1-5 stars
3. Add optional comments about what was wrong
4. Submit to help train the system for your needs

### Reset Options

If you need to reset parts of the system:

1. Go to **Settings → Data Management**
2. Choose what to reset:
   - Specific task type estimates
   - Stressor detection calibration
   - Buffer preferences
   - All time estimation data

## Tips and Best Practices

### For Better Estimates

- Use consistent task naming conventions
- Break down tasks larger than 2 hours into smaller steps
- Log start and end times accurately
- Note any unusual circumstances that affected duration

### For Productive Scheduling

- Schedule similar tasks together to reduce transition costs
- Place high-focus tasks during your peak energy periods
- Use buffer time intentionally for recovery
- Review next day's schedule before ending work

### For Managing Hyperfocus

- Set maximum duration limits for enjoyable tasks
- Schedule explicit transition activities after hyperfocus-prone tasks
- Use timer visualization during tasks
- Enable stronger notifications for hyperfocus sessions

### For Handling Procrastination

- Use the "Just 5 Minutes" feature to get started
- Break intimidating tasks into tiny next actions
- Schedule challenging tasks when your stressor level is lowest
- Use body doubling with the virtual co-working feature

## FAQ

### General Questions

**Q: How long before the estimates become accurate for me?**
A: Most users see significant improvement after 2-3 weeks of regular use. Task types you perform frequently will have more accurate estimates sooner.

**Q: Can I use this without a wearable device?**
A: Yes! Wearable devices provide additional data but aren't required. The system works well with just your task history and manual context inputs.

**Q: Will my personal data be used to help others?**
A: Only if you opt in to anonymized data sharing in settings. Your privacy is protected, and you can opt out at any time.

### Task Estimation

**Q: Why is there such a wide range between minimum and maximum estimates?**
A: This reflects the real variability in how long tasks take with ADHD. As the system learns your patterns, the range will narrow for task types with consistent completion times.

**Q: How does the system handle totally new tasks?**
A: It analyzes the description, looks for similar tasks in your history, and leverages anonymized data from similar users who have performed comparable tasks.

**Q: Can I manually adjust an estimate?**
A: Yes! Tap the estimate and select "Adjust." You can set your own expected duration, but the system will still show confidence intervals based on your history.

### Feature Specific

**Q: What's the difference between a buffer and padding?**
A: Buffers are explicit transition times between tasks. Padding is automatically added to task duration estimates to account for your historical completion patterns.

**Q: How do I temporarily disable stressor detection?**
A: Go to the Control Center and toggle "Pause Stressor Detection." You can set a duration for this pause or turn it back on manually.

**Q: Can I export my time estimation data?**
A: Yes! Go to Settings → Data Export and select the date range and data types you want to export. Data is available in CSV and JSON formats.

---

We hope this guide helps you make the most of the Stochastic Time Estimation Engine. Remember, the system is designed to adapt to your unique ADHD profile and improve over time. For additional help, visit our support portal or contact our assistance team.
