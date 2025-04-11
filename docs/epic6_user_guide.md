# ADHD Calendar: Epic 6 User Guide

**Version**: 1.0
**Last Updated**: 2025-03-15
**Target Audience**: End users of the ADHD Calendar application

## Introduction

This user guide provides detailed instructions on how to use the User Experience and Interface Optimization features of the ADHD Calendar application. Epic 6 introduces significant enhancements designed specifically to improve the application's usability for individuals with ADHD, including adaptive gamification, project management integrations, accessibility features, and calendar synchronization.

## Table of Contents

1. [Adaptive Gamification Features](#adaptive-gamification-features)
2. [Project Management Tool Integration](#project-management-tool-integration)
3. [Neurodiverse-Optimized UI](#neurodiverse-optimized-ui)
4. [Calendar Integration](#calendar-integration)
5. [Frequently Asked Questions](#frequently-asked-questions)

## Adaptive Gamification Features

The ADHD Calendar now includes personalized gamification elements that adapt to your unique motivation patterns, helping you stay engaged with tasks and build consistent habits.

### Motivation Profile

Your personal motivation profile helps the system understand what types of rewards and incentives work best for you.

#### Viewing Your Profile

1. Navigate to **Settings > Motivation Profile**
2. Review your current profile, including:
   - Primary and secondary motivators
   - Effective game mechanics
   - Reward preferences
   - Engagement patterns

![Motivation Profile Screen](../assets/motivation_profile.png)

#### Customizing Your Profile

1. On the Motivation Profile screen, click **Edit Profile**
2. Adjust the sliders for different motivators based on what resonates with you
3. Choose preferred mechanics and reward types
4. Click **Save** to update your profile

The system will use this information to personalize your experience, but will also learn and adapt automatically based on your interactions.

### Gamification Elements

The application includes several gamification elements that appear throughout your experience:

#### Streaks

Streaks track consecutive days of completing planned tasks or using the app.

![Streak Calendar](../assets/streak_calendar.png)

- **View Streaks**: On your dashboard, the streak counter shows your current streak
- **Streak Rewards**: Reach milestone streaks (3, 7, 14, 30 days) to earn special badges
- **Recover Streaks**: If you miss a day, you have a 24-hour grace period to recover your streak by completing a task

#### Badges and Achievements

Badges recognize your accomplishments and progress.

![Badges Collection](../assets/badges_collection.png)

- **View Badges**: Go to **Profile > Achievements** to see your badge collection
- **Badge Categories**: Badges are organized by category (Focus, Organization, Consistency)
- **Badge Levels**: Many badges have levels (Bronze, Silver, Gold) for progressive achievement

#### Progress Bars

Progress indicators help visualize your advancement toward goals.

- **Task Progress**: Each task shows a progress indicator when in progress
- **Daily Goals**: The dashboard displays your progress toward daily goals
- **Level Progress**: Your user level increases as you accumulate points

### Customizing Gamification

You can adjust how prominently gamification elements appear in your experience:

1. Go to **Settings > Gamification Preferences**
2. Adjust the **Gamification Intensity** slider (Subtle, Moderate, Prominent)
3. Toggle specific elements on or off (Streaks, Badges, Points, Leaderboards)
4. Set **Notification Preferences** for achievements and milestones

## Project Management Tool Integration

The ADHD Calendar now connects with popular project management tools to keep your tasks synchronized across platforms.

### Connecting a Project Management Tool

1. Go to **Settings > Integrations > Project Tools**
2. Click **Add Project Tool**
3. Select from supported platforms (Jira, Trello, Asana, etc.)
4. Follow the authentication steps for your selected platform
5. Choose which projects to sync
6. Select sync frequency and settings
7. Click **Connect**

![Project Tool Connection](../assets/project_tool_connection.png)

### Managing Task Synchronization

Once connected, you can manage how tasks sync between systems:

#### Two-Way Sync Settings

1. Go to **Settings > Integrations > Project Tools**
2. Select a connected tool
3. Under **Sync Settings**, choose:
   - **One-way import**: Only import tasks from the external tool
   - **One-way export**: Only export tasks to the external tool
   - **Two-way sync**: Synchronize tasks in both directions
4. Configure **Field Mapping** to control how task attributes map between systems

#### Manual Synchronization

To manually trigger synchronization:

1. Go to **Tasks > External Tasks**
2. Click the **Sync Now** button
3. View the sync status and any conflicts

### Working with External Tasks

Tasks from external tools appear alongside your regular tasks:

![External Tasks View](../assets/external_tasks.png)

- **Visual Indicators**: External tasks show an icon indicating their source
- **Conflict Resolution**: If a task is modified in both systems, you'll be prompted to resolve conflicts
- **Creating External Tasks**: When creating a task, you can choose to create it in an external tool as well

## Neurodiverse-Optimized UI

The ADHD Calendar now offers comprehensive UI customization options designed specifically for neurodiverse users.

### Accessibility Preferences

To access and customize your UI settings:

1. Go to **Settings > Accessibility**
2. Configure preferences in the following categories:

#### Visual Settings

- **Color Mode**: Choose from Standard, High Contrast, Reduced Blue Light, or Focus Mode
- **Text Size**: Adjust the size of text throughout the application
- **Reduce Motion**: Minimize animations and transitions
- **Reduce Transparency**: Make interface elements more opaque
- **Spacing Scale**: Adjust the spacing between elements

![Visual Settings](../assets/accessibility_visual.png)

#### Focus Assistance

- **Reduce Distractions**: Hide non-essential UI elements
- **Highlight Focus**: Emphasize the currently focused element
- **Reading Guide**: Enable a guide that helps maintain focus while reading
- **Focus Timers**: Set automatic reminders to check focus

#### Font Settings

- **Custom Fonts**: Enable specialized fonts for reading ease
- **Font Family**: Choose from standard or dyslexia-friendly fonts
- **Line Spacing**: Adjust the spacing between lines of text

### ADHD-Optimized Presets

For quick setup, you can use pre-configured settings optimized for different ADHD types:

1. Go to **Settings > Accessibility > Presets**
2. Choose from:
   - **Inattentive Preset**: Emphasizes focus tools and reduces distractions
   - **Hyperactive Preset**: Provides more interactive elements and frequent breaks
   - **Combined Preset**: Balanced approach for combined ADHD type

### Context-Aware Adaptations

The UI can adapt automatically based on your context:

- **Time of Day**: Shifts to blue light reduction in evening hours
- **Energy Level**: Adjusts complexity based on reported energy level
- **Task Type**: Optimizes interface based on current task requirements

To enable context-aware adaptations:

1. Go to **Settings > Accessibility > Context Adaptations**
2. Toggle on the adaptations you want to enable
3. Configure the sensitivity and thresholds for each adaptation

## Calendar Integration

The ADHD Calendar now integrates with external calendar systems to provide a unified view of your schedule.

### Connecting a Calendar

1. Go to **Settings > Integrations > Calendars**
2. Click **Add Calendar**
3. Select from supported platforms (Google, Apple, Outlook, etc.)
4. Follow the authentication steps for your selected platform
5. Choose which calendars to sync
6. Configure sync settings
7. Click **Connect**

![Calendar Connection](../assets/calendar_connection.png)

### Managing Calendar Synchronization

Once connected, you can manage how events sync between systems:

#### Sync Settings

1. Go to **Settings > Integrations > Calendars**
2. Select a connected calendar
3. Configure:
   - **Sync Frequency**: How often calendars should sync (15 min, 30 min, hourly)
   - **Event Details**: Whether to include full details or just times
   - **Color Coding**: Maintain color coding from external calendar
   - **Default Reminders**: Set default reminder times for imported events

![Calendar Sync Settings](../assets/calendar_sync_settings.png)

#### Selective Syncing

You can choose which external calendars and event types to include:

1. Go to **Settings > Integrations > Calendars > [Your Calendar]**
2. Under **Calendars to Sync**, select specific sub-calendars
3. Under **Event Filters**, choose event types to include or exclude

### Working with Calendar Events

External calendar events appear alongside your ADHD Calendar events:

![Unified Calendar View](../assets/unified_calendar.png)

- **Visual Indicators**: External events show an icon indicating their source
- **Creating Events**: When creating an event, you can choose which calendar to add it to
- **Event Details**: Click on any event to view or edit its details
- **Context Menu**: Right-click an event for quick actions

## Frequently Asked Questions

### Adaptive Gamification

**Q: Can I turn off gamification completely?**
A: Yes, go to Settings > Gamification Preferences and toggle "Enable Gamification" to off.

**Q: How does the system learn my motivation patterns?**
A: The system analyzes which gamification elements you engage with most, what rewards motivate task completion, and your usage patterns over time.

**Q: Can I reset my motivation profile?**
A: Yes, go to Settings > Motivation Profile > Reset Profile to start fresh.

### Project Management Integration

**Q: What project tools are currently supported?**
A: We currently support Jira, Trello, Asana, Monday.com, and ClickUp. More integrations are being added regularly.

**Q: How often do tasks sync automatically?**
A: The default is every 30 minutes, but you can configure this from 15 minutes to 24 hours.

**Q: What happens if I update a task in both systems?**
A: You'll receive a conflict notification and can choose which version to keep, or merge changes.

### Neurodiverse-Optimized UI

**Q: Do my accessibility settings sync across devices?**
A: Yes, all settings are tied to your user account and will apply on any device you sign in to.

**Q: Can I schedule different UI settings for different times of day?**
A: Yes, enable Context Adaptations and configure time-based settings under Settings > Accessibility > Context Adaptations > Time-Based Settings.

**Q: How do I find the best accessibility settings for my needs?**
A: Try the ADHD preset that matches your type, then adjust individual settings based on your preferences.

### Calendar Integration

**Q: Can I edit external calendar events in the ADHD Calendar?**
A: Yes, if you've enabled two-way sync and have appropriate permissions for the external calendar.

**Q: What happens if I delete an external event?**
A: If two-way sync is enabled, the event will be deleted from the external calendar as well. You'll receive a confirmation prompt before deletion.

**Q: Do task due dates appear on my external calendars?**
A: This is configurable. Go to Settings > Integrations > Calendars > Task Integration to control whether and how tasks appear on external calendars.

## Getting Help

If you have questions about these new features:
- View interactive tutorials in the **Help > Feature Tours** section
- Contact support through the **Help > Contact** menu
- Join our user community at **community.adhdcalendar.com**

We've designed these features with input from ADHD users at every stage, and we welcome your feedback to make them even better.

---

© 2025 ADHD Calendar - Empowering focus through intuitive design
