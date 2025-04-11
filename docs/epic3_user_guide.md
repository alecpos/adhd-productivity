# Epic 3: User Guide - Proactive Forgetfulness and Distraction Mitigation

This guide provides an overview of the Epic 3 features designed to help ADHD users manage forgetfulness and distraction. These features work together to create a comprehensive support system for keeping track of commitments and important tasks.

## Table of Contents

1. [Commitment Detection](#commitment-detection)
2. [Dialogue System ("Forgot Anything?")](#dialogue-system-forgot-anything)
3. [Smart Reminder System](#smart-reminder-system)
4. [Integration with Other Tools](#integration-with-other-tools)
5. [Accessibility Features](#accessibility-features)
6. [Advanced Usage Techniques](#advanced-usage-techniques)
7. [Frequently Asked Questions](#frequently-asked-questions)
8. [Getting Help](#getting-help)

## Commitment Detection

### Overview

The commitment detection system automatically identifies promises and obligations from your text input, helping you keep track of what you've committed to do without requiring manual entry.

### Key Features

- **Automatic Detection**: Commitments are automatically extracted from journal entries, notes, chat messages, and emails
- **Explicit & Implicit Detection**: Recognizes both clear promises ("I will call John") and implied commitments ("Maybe I should email Sarah")
- **Temporal Extraction**: Automatically identifies due dates and time frames from context
- **Priority Classification**: Assigns priority based on language, urgency, and importance
- **De-duplication**: Recognizes and merges similar commitments to prevent clutter

### How It Works

When you write or speak text containing a commitment:

1. The system analyzes your text in real-time
2. It identifies commitment language patterns
3. It extracts relevant details (what, when, priority)
4. The commitment is saved to your personal commitment tracker
5. It becomes available for reminders and review

### Example Scenarios

| When you write/say... | The system detects... |
|-----------------------|----------------------|
| "I'll send the report by Friday" | Commitment: "send the report"<br>Due date: This Friday<br>Priority: Medium |
| "I should probably call mom sometime" | Commitment: "call mom"<br>Time frame: Flexible/Undefined<br>Priority: Low |
| "I MUST submit the application before the deadline on Tuesday!" | Commitment: "submit the application"<br>Due date: Tuesday<br>Priority: High |

### Privacy Considerations

- Text analysis happens on your device when possible
- You can review and delete detected commitments at any time
- You can disable automatic detection for specific sources

### Customizing Commitment Detection

You can customize how the system detects commitments through the Settings menu:

1. Go to **Settings > Commitment Detection**
2. Adjust the following options:
   - **Detection Sensitivity**: Control how aggressively the system identifies potential commitments
   - **Source Monitoring**: Enable/disable detection from specific sources (email, chat, notes)
   - **Priority Thresholds**: Customize what words or phrases indicate different priority levels
   - **Personal Dictionary**: Add custom words or phrases that indicate commitments in your language
   - **False Positive Training**: Mark incorrectly detected commitments to improve accuracy

## Dialogue System ("Forgot Anything?")

### Overview

The "Forgot Anything?" dialogue system provides a conversational interface to help you remember and manage your commitments through natural language interaction.

### Key Features

- **Natural Conversation**: Interact using everyday language
- **Contextual Awareness**: System remembers conversation context
- **Commitment Integration**: Direct access to your commitment tracker
- **Real-time Detection**: Identifies new commitments during conversation
- **Helpful Suggestions**: Provides actionable next steps

### How to Use

#### Accessing the Dialogue System

1. Click the "Forgot Anything?" button in the app header
2. Use the chat widget in the bottom-right corner
3. Use voice commands (if enabled): "Hey ADHD Calendar, did I forget anything?"

#### Example Conversations

**Checking Today's Commitments**:

```
You: What do I need to do today?
System: You have 3 commitments today:
1. Submit the quarterly report (due at 5pm)
2. Call John about the project (anytime today)
3. Pick up groceries (on your way home)

Would you like to see details for any of these?
```

**Adding a New Commitment**:

```
You: I need to email Sarah about the meeting tomorrow.
System: I've detected a new commitment: "email Sarah about the meeting" due tomorrow.
Would you like me to add this to your commitments?

You: Yes, please.
System: Great! I've added it to your commitments with medium priority.
Would you like a reminder?
```

**Getting Help with Priorities**:

```
You: I'm feeling overwhelmed. What should I focus on?
System: Based on urgency and importance, here are your top 3 priorities:
1. Submit the quarterly report (due in 2 hours)
2. Prepare for tomorrow's presentation (due tomorrow at 9am)
3. Email Sarah about the meeting (due tomorrow)

Shall I help you break down any of these tasks?
```

### Tips for Effective Use

- Be specific when asking questions
- Start with phrases like "What should I...", "Did I forget...", "When do I..."
- Use the dialogue system regularly to build the habit of checking commitments
- Give feedback when suggestions aren't helpful to improve personalization

### Personalization Options

The dialogue system can be personalized to better match your needs:

1. Go to **Settings > Dialogue System**
2. Adjust the following options:
   - **Conversation Style**: Choose between Direct (brief, to-the-point), Supportive (encouraging, positive), or Detailed (comprehensive information)
   - **Proactive Reminders**: Control when the system reaches out to you unprompted
   - **Session Memory**: Adjust how long the system maintains context between conversations
   - **Voice Settings**: Customize voice interaction options and trigger phrases
   - **Smart Suggestions**: Control the types of suggestions the system offers

## Smart Reminder System

### Overview

The smart reminder system provides contextually-aware reminders that adapt to your situation, helping you remember commitments at the right time and place.

### Key Features

- **Contextual Awareness**: Delivers reminders based on time, location, and activity
- **Priority-Based Delivery**: Focuses on what's most important right now
- **Adaptive Timing**: Learns optimal reminder times based on your response patterns
- **Minimized Interruptions**: Groups related reminders to reduce distraction
- **Actionable Notifications**: Take action directly from reminder notifications

### How It Works

1. The system continuously evaluates your commitments
2. It considers factors like:
   - Due date and time
   - Commitment priority
   - Your current context (location, activity)
   - Past reminder effectiveness
3. It delivers reminders at optimal moments
4. It tracks your response to improve future reminders

### Types of Reminders

| Reminder Type | Description | Example |
|---------------|-------------|---------|
| **Time-based** | Tied to specific times or deadlines | "Meeting with Alex in 30 minutes" |
| **Location-based** | Triggered when entering relevant locations | "Pick up groceries" when near the store |
| **Activity-based** | Linked to specific activities | "Call John" when you finish your current meeting |
| **Priority alerts** | For high-priority, urgent commitments | "Urgent: Submit report (due in 1 hour)" |

### Customizing Your Reminders

You can customize the smart reminder system through the Settings menu:

1. **Reminder Frequency**: Adjust how often you receive reminders
2. **Notification Style**: Choose between subtle, standard, or prominent alerts
3. **Quiet Hours**: Set times when only high-priority reminders are delivered
4. **Location Awareness**: Enable/disable location-based reminders
5. **Learning Rate**: Control how quickly the system adapts to your patterns

### Best Practices

- Respond to reminders (even to dismiss them) to help the system learn
- Use the "Snooze" option rather than ignoring reminders
- Review the "Reminder Effectiveness" report weekly to optimize settings
- Provide priority information when creating commitments for better reminder delivery

### Advanced Reminder Settings

For more detailed control, access advanced settings:

1. Go to **Settings > Smart Reminders > Advanced**
2. Customize:
   - **Channel Preferences**: Set different notification channels (push, email, SMS) for different priority levels
   - **Escalation Rules**: Configure how reminders escalate if ignored
   - **Notification Grouping**: Set rules for grouping similar reminders
   - **Postponement Behavior**: Control what happens when you snooze reminders
   - **Success Tracking**: Define what counts as successful completion

## Integration with Other Tools

The Epic 3 features integrate with various tools and services to provide a seamless experience.

### Calendar Integration

- **Two-way Sync**: Commitments can automatically create calendar events
- **Smart Scheduling**: The system can suggest optimal times to schedule commitment-related tasks
- **Meeting Context**: Calendar meetings provide context for commitment reminders
- **Setup**: Go to **Settings > Integrations > Calendar** and select your calendar service

### Task Management Integration

- **Task Conversion**: Convert commitments to tasks in your preferred task manager
- **Status Synchronization**: Task completion status syncs back to commitment status
- **Priority Alignment**: Task priorities align with commitment priorities
- **Supported Apps**: Integrates with Todoist, Asana, Microsoft To Do, and more
- **Setup**: Go to **Settings > Integrations > Task Managers**

### Communication Tool Integration

- **Email Integration**: Detect commitments from Gmail, Outlook, and other email services
- **Chat Platform Support**: Works with Slack, Microsoft Teams, and Discord
- **Meeting Note Analysis**: Scan meeting notes from Zoom, Google Meet, etc.
- **Setup**: Go to **Settings > Integrations > Communication Tools**

### Smart Home & Voice Assistant Integration

- **Voice Assistants**: Ask Alexa, Google Assistant, or Siri about your commitments
- **Smart Displays**: Show commitment summaries on Echo Show, Nest Hub, etc.
- **Routine Integration**: Include commitment checks in your morning routine
- **Setup**: Go to **Settings > Integrations > Smart Home & Voice**

### API Access for Developers

- **REST API**: Access commitments and reminders programmatically
- **Webhook Support**: Receive real-time notifications for commitment events
- **Custom Integrations**: Build your own tools using our developer resources
- **Documentation**: Available at developer.adhdcalendar.com

## Accessibility Features

The Epic 3 features are designed to be accessible to users with diverse needs.

### Visual Accessibility

- **Screen Reader Support**: All features are fully compatible with screen readers
- **High Contrast Mode**: Enhanced visual contrast for better readability
- **Text Size Adjustment**: Customize text size throughout the interface
- **Color Blind Modes**: Alternative color schemes for different types of color vision
- **Setup**: Go to **Settings > Accessibility > Visual**

### Auditory Accessibility

- **Text-to-Speech**: Have commitments and reminders read aloud
- **Custom Sound Profiles**: Different sounds for different priority levels
- **Volume Control**: Independent volume settings for different notification types
- **Setup**: Go to **Settings > Accessibility > Auditory**

### Motor Accessibility

- **Keyboard Navigation**: Full functionality without requiring mouse or touch
- **Voice Control**: Complete hands-free operation using voice commands
- **Gesture Customization**: Simplified gesture controls for touchscreen users
- **Setup**: Go to **Settings > Accessibility > Motor**

### Cognitive Accessibility

- **Simplified Interface**: Option for reduced clutter and simpler interactions
- **Step-by-Step Guidance**: Interactive tutorials for all features
- **Customizable Terminology**: Adjust language complexity to your preference
- **Focus Mode**: Temporarily reduce distractions in the interface
- **Setup**: Go to **Settings > Accessibility > Cognitive**

### Language Support

- **Multilingual Interface**: Available in 12 languages
- **Commitment Detection**: Language-specific detection for 8 major languages
- **Translation Services**: Auto-translate commitments between languages
- **Setup**: Go to **Settings > Accessibility > Language**

## Advanced Usage Techniques

These techniques help power users get the most out of the Epic 3 features.

### Commitment Tagging and Filtering

- **Custom Tags**: Create personalized tags for organizing commitments
- **Smart Filters**: Build saved filters combining multiple criteria
- **Bulk Actions**: Apply changes to multiple commitments at once
- **How to**: Go to **Commitments > Manage Tags** to set up your tagging system

### Context-Based Views

- **Activity Contexts**: Group commitments by activity (work, home, errands)
- **Energy Level Matching**: Assign energy requirements to commitments and match to your current state
- **Focus Sessions**: Create distraction-free focus periods with deferred reminders
- **How to**: Use the **Context Filters** in the commitment dashboard

### Data Analysis and Insights

- **Completion Metrics**: Track your commitment completion rates
- **Pattern Recognition**: Identify your most productive times and contexts
- **Stress Indicators**: Monitor commitment load and potential overcommitment
- **How to**: Visit the **Insights** tab in the dashboard

### Collaborative Commitments

- **Shared Commitments**: Create commitments visible to teammates or family
- **Accountability Partners**: Designate someone to help keep you on track
- **Status Updates**: Automatically notify others of commitment progress
- **How to**: Use the **Share** option when creating or editing a commitment

### Commitment Templates

- **Reusable Templates**: Create templates for common commitment types
- **Quick Entry**: Rapidly create commitments based on templates
- **Suggested Fields**: Smart suggestions based on commitment type
- **How to**: Go to **Settings > Commitment Detection > Templates**

### Backup and Export

- **Data Export**: Export your commitments in various formats (CSV, JSON)
- **Backup Settings**: Create backups of your personalized settings
- **Cross-Device Sync**: Synchronize settings across multiple devices
- **How to**: Go to **Settings > Data Management**

## Frequently Asked Questions

### General Questions

**Q: How accurate is the commitment detection?**
A: The system achieves 87% precision in detecting explicit commitments and 82% recall overall. It works best with clear, specific language but can also detect many implicit commitments.

**Q: Can I edit detected commitments?**
A: Yes, you can edit any aspect of a detected commitment (text, due date, priority) through the Commitments tab in the app.

**Q: Is my data private?**
A: Yes. All text analysis is done on-device when possible, and any server-side processing follows strict privacy protocols. Your commitments are only accessible to you and those you explicitly share with.

### Dialogue System

**Q: Can I use voice to interact with the dialogue system?**
A: Yes, if you enable voice interaction in Settings, you can use voice commands to start conversations and respond to the system.

**Q: How long does the system remember our conversation context?**
A: The system maintains context for the duration of a session (typically 30 minutes of active conversation) and remembers key topics across sessions.

**Q: Is the dialogue system available offline?**
A: Basic dialogue functionality works offline, but advanced features like commitment detection may have limited functionality without an internet connection.

### Smart Reminders

**Q: How does the system know when to remind me?**
A: It combines factors including due date, priority, your location, current activity, and past reminder effectiveness to determine optimal timing.

**Q: Will I get too many reminders if I have lots of commitments?**
A: No. The system intelligently groups related reminders and prioritizes to prevent overwhelming you, even with many commitments.

**Q: Can I share reminders with others?**
A: Yes, you can share specific commitments and their reminders with collaborators, family members, or your support network.

**Q: How can I stop getting reminders for a specific commitment?**
A: You can either mark the commitment as completed, mute reminders temporarily, or adjust the reminder settings for that specific commitment.

### Integration and Data

**Q: Can I import commitments from other task managers?**
A: Yes, you can import tasks from popular task managers through the Data Management section in Settings.

**Q: Does the system work with calendar invitations?**
A: Yes, calendar events are automatically considered when scheduling reminders to avoid conflicts.

**Q: What happens if I use multiple devices?**
A: All your data syncs across devices. Detection settings can be configured globally or per-device.

## Getting Help

If you need assistance with any Epic 3 features:

- **In-app Help**: Tap the "?" icon in any screen for contextual help
- **Help Center**: Visit help.adhdcalendar.com for comprehensive guides
- **Email Support**: Contact support@adhdcalendar.com for personalized assistance
- **Community Forums**: Join discussions at community.adhdcalendar.com
- **Video Tutorials**: Watch our tutorial series on YouTube
- **Webinars**: Attend monthly live training sessions (schedule in app)
- **1-on-1 Training**: Premium users can schedule personalized training sessions

### Reporting Issues

If you encounter any problems:

1. Go to **Settings > Support > Report Issue**
2. Describe the problem in detail
3. Include screenshots if relevant
4. Submit the report

Our support team typically responds within 24 hours.

### Feature Requests

Have ideas for improvement? We'd love to hear them:

1. Go to **Settings > Support > Feature Request**
2. Describe your idea and how it would help you
3. Vote on existing feature requests
4. Track the status of your requests in the Support portal
