# ADHD Calendar: Epic 6 Integration Guide

**Version**: 1.0  
**Last Updated**: 2025-03-15  
**Target Audience**: Developers integrating with ADHD Calendar UX components

## Overview

This integration guide provides detailed instructions for developers who want to integrate with the User Experience and Interface Optimization components of the ADHD Calendar platform. Epic 6 introduces several powerful new systems that can be leveraged by third-party applications, extensions, and custom implementations.

## Table of Contents

1. [Integration Architecture](#integration-architecture)
2. [Adaptive Gamification Integration](#adaptive-gamification-integration)
3. [Project Management Tool Integration](#project-management-tool-integration)
4. [Accessibility Framework Integration](#accessibility-framework-integration)
5. [Calendar System Integration](#calendar-system-integration)
6. [Security and Authentication](#security-and-authentication)
7. [Testing and Validation](#testing-and-validation)

## Integration Architecture

### Overall Architecture

The Epic 6 components are designed with a modular architecture that allows for various integration approaches:

```
┌─────────────────────────────────────────────────────────────────────┐
│                       Your Application                               │
└───┬───────────────────┬───────────────────┬───────────────────┬─────┘
    │                   │                   │                   │
    ▼                   ▼                   ▼                   ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│ Gamification│   │  Project    │   │Accessibility│   │  Calendar   │
│     API     │   │Management API   │    API     │   │     API     │
└─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘
        │               │                 │                 │
        ▼               ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    ADHD Calendar Platform                            │
└─────────────────────────────────────────────────────────────────────┘
```

### Integration Methods

There are several approaches to integrating with Epic 6 components:

1. **REST API Integration**: The primary method for most integrations, providing full access to all features
2. **JavaScript SDK**: For web-based integrations that need direct UI integration
3. **Webhook Integration**: For event-driven architectures that need to respond to ADHD Calendar events
4. **OAuth 2.0 App Integration**: For full-featured applications requiring user authentication

### Authentication

All integrations require authentication using one of the following methods:

- **API Keys**: For server-to-server integrations
- **OAuth 2.0**: For applications acting on behalf of users
- **JWT Tokens**: For microservice-to-microservice communication

API keys can be generated in the ADHD Calendar Developer Portal.

## Adaptive Gamification Integration

The Adaptive Gamification system provides powerful motivation tools that can be integrated into external applications.

### Key Integration Points

1. **User Motivation Profiles**: Access and update user motivation data
2. **Gamification Actions**: Trigger motivation-appropriate gamification elements
3. **Effectiveness Tracking**: Report user engagement with gamification elements

### User Motivation Profile Integration

#### Retrieving User Profiles

To retrieve a user's motivation profile:

```javascript
// JavaScript SDK Example
const adhd = require('adhd-calendar-sdk');

async function getUserMotivationProfile(userId) {
  const client = new adhd.GamificationClient(apiKey);
  const profile = await client.getUserMotivationProfile(userId);
  
  console.log(`Primary motivators: ${profile.primary_motivators.join(', ')}`);
  console.log(`Effective mechanics: ${profile.effective_mechanics.join(', ')}`);
  
  return profile;
}
```

```python
# Python SDK Example
from adhd_calendar import GamificationClient

def get_user_motivation_profile(user_id):
    client = GamificationClient(api_key)
    profile = client.get_user_motivation_profile(user_id)
    
    print(f"Primary motivators: {', '.join(profile.primary_motivators)}")
    print(f"Effective mechanics: {', '.join(profile.effective_mechanics)}")
    
    return profile
```

#### Updating User Profiles

To update specific aspects of a motivation profile:

```javascript
// JavaScript SDK Example
async function updateUserMotivationProfile(userId, updates) {
  const client = new adhd.GamificationClient(apiKey);
  const updatedProfile = await client.updateUserMotivationProfile(userId, updates);
  
  return updatedProfile;
}

// Example usage
updateUserMotivationProfile('user123', {
  primary_motivators: ['achievement', 'creativity'],
  reward_preferences: ['progressive', 'milestone']
});
```

### Gamification Actions Integration

#### Requesting Optimal Gamification Actions

To get recommended gamification actions for a specific context:

```javascript
// JavaScript SDK Example
async function getRecommendedActions(userId, context, count = 2) {
  const client = new adhd.GamificationClient(apiKey);
  const actions = await client.getGamificationActions(userId, context, count);
  
  return actions;
}

// Example usage
const context = {
  task_type: 'focus',
  difficulty: 0.7,
  importance: 0.8,
  energy_level: 0.6
};

getRecommendedActions('user123', context).then(actions => {
  actions.forEach(action => {
    console.log(`Recommended action: ${action.name} - ${action.description}`);
  });
});
```

#### Implementing Action Presentation

When presenting gamification actions, follow these best practices:

1. Respect the user's gamification intensity preferences
2. Present actions at appropriate moments (task completion, session start, etc.)
3. Use consistent visual design for similar mechanics
4. Provide clear ways to dismiss or postpone gamification elements

Example UI implementation for a streak mechanic:

```jsx
// React component example
function StreakDisplay({ streak, milestones }) {
  const nextMilestone = milestones.find(m => m > streak) || streak + 5;
  
  return (
    <div className="streak-container">
      <div className="streak-count">{streak}</div>
      <div className="streak-label">Day Streak</div>
      <div className="streak-progress">
        <div 
          className="streak-bar" 
          style={{ width: `${(streak % nextMilestone) / nextMilestone * 100}%` }}
        />
      </div>
      <div className="streak-next">Next reward in {nextMilestone - streak} days</div>
    </div>
  );
}
```

#### Tracking Effectiveness

To report user engagement with gamification actions:

```javascript
// JavaScript SDK Example
async function trackActionEffectiveness(userId, actionId, metrics) {
  const client = new adhd.GamificationClient(apiKey);
  const result = await client.trackEffectiveness(userId, actionId, metrics);
  
  return result;
}

// Example usage
trackActionEffectiveness('user123', 'action456', {
  engagement_score: 0.85,
  interaction_type: 'clicked',
  task_completed: true,
  time_spent: 120
});
```

### UI Component Library

For web integrations, we provide pre-built UI components for common gamification elements:

```javascript
// React component library example
import { 
  StreakCounter, 
  BadgeDisplay, 
  ProgressBar,
  AchievementPopup 
} from 'adhd-gamification-react';

function MyApp() {
  return (
    <div className="app">
      <StreakCounter userId="user123" theme="minimal" />
      
      <BadgeDisplay 
        userId="user123" 
        category="focus" 
        layout="grid" 
      />
      
      <ProgressBar 
        value={75} 
        target={100} 
        label="Daily Goal" 
        style="segmented" 
      />
      
      <AchievementPopup 
        onAchievement={handleAchievement} 
        position="bottom-right" 
      />
    </div>
  );
}
```

## Project Management Tool Integration

### Integration Types

The Project Management integration supports three approaches:

1. **Existing Tool Integration**: Connecting with an already supported tool like Jira or Trello
2. **Custom Tool Integration**: Creating a connector for a custom project management system
3. **Embedding ADHD Calendar**: Embedding ADHD Calendar functionality within your project tool

### Integrating With Existing Tools

If your application needs to leverage ADHD Calendar's connections with existing project tools:

```javascript
// JavaScript SDK Example
async function syncExternalTasks(userId, toolId) {
  const client = new adhd.ProjectToolsClient(apiKey);
  const result = await client.syncTasks(userId, toolId);
  
  console.log(`Synced ${result.tasks_added} new tasks and updated ${result.tasks_updated} tasks`);
  
  return result;
}

// Get tasks from a specific tool
async function getExternalTasks(userId, toolId, filters = {}) {
  const client = new adhd.ProjectToolsClient(apiKey);
  const tasks = await client.getTasks(userId, toolId, filters);
  
  return tasks;
}
```

### Creating a Custom Tool Connector

To build a connector for a new project management tool:

1. Implement the `ProjectManagementIntegration` interface
2. Register your connector with the ADHD Calendar platform
3. Create authentication flows for users to connect to your tool

Example connector implementation:

```javascript
// JavaScript implementation example
class MyCustomToolConnector extends adhd.ProjectManagementIntegration {
  constructor(config) {
    super();
    this.apiUrl = config.apiUrl;
    this.apiKey = config.apiKey;
  }
  
  async authenticate(credentials) {
    // Implement authentication with your tool
    // Return true if successful, false otherwise
  }
  
  async fetchTasks(since = null) {
    // Fetch tasks from your system
    // Transform them to ExternalTask format
    return transformedTasks;
  }
  
  async createTask(taskData) {
    // Create a task in your system
    // Return the created task in ExternalTask format
  }
  
  async updateTask(externalId, taskData) {
    // Update a task in your system
    // Return the updated task in ExternalTask format
  }
  
  async deleteTask(externalId) {
    // Delete a task in your system
    // Return true if successful, false otherwise
  }
  
  async getProjects() {
    // Return list of available projects
  }
}

// Register the connector
adhd.registerProjectTool('my-custom-tool', MyCustomToolConnector);
```

### Tool Registration Process

To register a custom tool connector:

1. Register as a developer at the ADHD Calendar Developer Portal
2. Submit your connector for review
3. Provide documentation for your connector
4. Once approved, users can select your tool from the integration options

## Accessibility Framework Integration

The Accessibility Framework provides tools for creating ADHD-friendly user interfaces that can be integrated into your applications.

### Integrating Accessibility Preferences

To access a user's accessibility preferences:

```javascript
// JavaScript SDK Example
async function getUserAccessibilityPreferences(userId) {
  const client = new adhd.AccessibilityClient(apiKey);
  const preferences = await client.getUserPreferences(userId);
  
  return preferences;
}
```

### Using the CSS Theme Generator

To generate custom CSS based on accessibility preferences:

```javascript
// JavaScript SDK Example
async function getAccessibilityCSS(userId, context = 'default') {
  const client = new adhd.AccessibilityClient(apiKey);
  const css = await client.getThemeCSS(userId, context);
  
  // Inject the CSS into your application
  const styleElement = document.createElement('style');
  styleElement.textContent = css;
  document.head.appendChild(styleElement);
}
```

### Implementing Focus Assistance

To add focus assistance features to your application:

```javascript
// JavaScript SDK Example
import { 
  FocusHighlighter, 
  ReadingGuide, 
  DistractionReducer 
} from 'adhd-accessibility-sdk';

// Initialize components with user preferences
async function initAccessibilityComponents(userId) {
  const client = new adhd.AccessibilityClient(apiKey);
  const preferences = await client.getUserPreferences(userId);
  
  // Initialize focus highlighter
  if (preferences.highlight_focus) {
    const highlighter = new FocusHighlighter({
      color: preferences.focus_color || '#ffcc00',
      intensity: preferences.focus_intensity || 0.5,
      transitionSpeed: preferences.reduce_motion ? 'none' : 'normal'
    });
    highlighter.attach();
  }
  
  // Initialize reading guide
  if (preferences.reading_guide) {
    const guide = new ReadingGuide({
      color: preferences.guide_color || 'rgba(255, 255, 0, 0.2)',
      height: preferences.guide_height || '1.5em',
      behavior: preferences.guide_behavior || 'follow'
    });
    guide.attach('article, .content, p');
  }
  
  // Initialize distraction reducer
  if (preferences.reduce_distractions) {
    const reducer = new DistractionReducer({
      dimOpacity: preferences.dim_opacity || 0.7,
      excludeSelectors: ['.main-content', 'nav', 'header']
    });
    reducer.attach();
  }
}
```

### Accessibility Testing Integration

To validate your application against ADHD accessibility guidelines:

```javascript
// JavaScript SDK Example
async function testAccessibilityCompliance(pageUrl) {
  const client = new adhd.AccessibilityClient(apiKey);
  const report = await client.testAccessibility(pageUrl);
  
  console.log(`Overall compliance: ${report.overall_compliance}`);
  
  report.issues.forEach(issue => {
    console.log(`${issue.severity}: ${issue.message} at ${issue.element}`);
  });
  
  return report;
}
```

## Calendar System Integration

### Connecting With Calendar Systems

To integrate with the Calendar System:

1. **OAuth Authentication**: Implement OAuth flow to connect with calendar providers
2. **Event Synchronization**: Sync events between systems
3. **Calendar Selection**: Allow users to choose which calendars to sync
4. **Conflict Resolution**: Handle event conflicts appropriately

### Implementing Calendar OAuth Flow

Example OAuth flow implementation:

```javascript
// JavaScript SDK Example
function initiateCalendarAuth(provider) {
  const client = new adhd.CalendarClient(apiKey);
  const authUrl = client.getAuthUrl(provider, {
    redirectUri: 'https://your-app.com/calendar/callback',
    scope: 'read_write'
  });
  
  // Redirect the user to the authentication URL
  window.location.href = authUrl;
}

// Handle the OAuth callback
async function handleCalendarAuthCallback(code) {
  const client = new adhd.CalendarClient(apiKey);
  const result = await client.completeAuth(code, {
    redirectUri: 'https://your-app.com/calendar/callback'
  });
  
  return result.calendarId;
}
```

### Syncing Calendar Events

To synchronize events with external calendars:

```javascript
// JavaScript SDK Example
async function syncCalendarEvents(userId, calendarId) {
  const client = new adhd.CalendarClient(apiKey);
  const result = await client.syncEvents(userId, calendarId, {
    startDate: new Date(),
    endDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), // 30 days
    fullSync: false
  });
  
  console.log(`Synced ${result.events_added} new events and updated ${result.events_updated} events`);
  
  return result;
}
```

### Creating and Managing Events

To create and manage calendar events:

```javascript
// JavaScript SDK Example
async function createCalendarEvent(userId, calendarId, eventData) {
  const client = new adhd.CalendarClient(apiKey);
  const event = await client.createEvent(userId, calendarId, eventData);
  
  return event;
}

async function updateCalendarEvent(userId, calendarId, eventId, eventData) {
  const client = new adhd.CalendarClient(apiKey);
  const event = await client.updateEvent(userId, calendarId, eventId, eventData);
  
  return event;
}

async function deleteCalendarEvent(userId, calendarId, eventId) {
  const client = new adhd.CalendarClient(apiKey);
  const result = await client.deleteEvent(userId, calendarId, eventId);
  
  return result.success;
}
```

### Calendar UI Components

For web applications, we provide pre-built calendar UI components:

```jsx
// React component example
import { 
  CalendarView, 
  EventDetails, 
  EventCreator 
} from 'adhd-calendar-react';

function MyCalendarApp({ userId }) {
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [selectedEvent, setSelectedEvent] = useState(null);
  
  return (
    <div className="calendar-container">
      <CalendarView 
        userId={userId}
        date={selectedDate}
        onDateChange={setSelectedDate}
        onEventSelect={setSelectedEvent}
        view="week"
        calendars={['google-work', 'apple-personal']}
      />
      
      {selectedEvent && (
        <EventDetails 
          userId={userId}
          event={selectedEvent}
          onEdit={handleEditEvent}
          onDelete={handleDeleteEvent}
        />
      )}
      
      <EventCreator 
        userId={userId}
        date={selectedDate}
        defaultDuration={60}
        availableCalendars={['google-work', 'apple-personal']}
        onEventCreate={handleCreateEvent}
      />
    </div>
  );
}
```

## Security and Authentication

### API Key Authentication

For server-to-server integrations, use API key authentication:

```javascript
// JavaScript SDK Example
const adhd = require('adhd-calendar-sdk');

// Initialize the client with your API key
const client = new adhd.Client({
  apiKey: 'your-api-key',
  environment: 'production' // or 'sandbox' for testing
});
```

### OAuth 2.0 Integration

For user-authorized applications, implement OAuth 2.0:

1. Register your application in the ADHD Calendar Developer Portal
2. Implement the OAuth 2.0 flow in your application
3. Use the obtained tokens to make API calls on behalf of users

```javascript
// JavaScript SDK Example
const adhd = require('adhd-calendar-sdk');

// Initialize OAuth client
const oauthClient = new adhd.OAuthClient({
  clientId: 'your-client-id',
  clientSecret: 'your-client-secret',
  redirectUri: 'https://your-app.com/callback'
});

// Generate the authorization URL
function getAuthUrl() {
  return oauthClient.getAuthorizationUrl({
    scope: 'user.profile gamification calendar project_tools accessibility',
    state: generateRandomState()
  });
}

// Handle the OAuth callback
async function handleCallback(code, state) {
  // Verify state to prevent CSRF attacks
  verifyState(state);
  
  // Exchange the code for tokens
  const tokens = await oauthClient.getTokens(code);
  
  // Initialize the API client with the access token
  const client = new adhd.Client({
    accessToken: tokens.access_token
  });
  
  // Store the refresh token securely
  securelyStoreRefreshToken(tokens.refresh_token);
  
  return client;
}

// Refresh the access token when it expires
async function refreshAccessToken(refreshToken) {
  const tokens = await oauthClient.refreshTokens(refreshToken);
  
  // Update the client with the new access token
  client.setAccessToken(tokens.access_token);
  
  // Store the new refresh token if provided
  if (tokens.refresh_token) {
    securelyStoreRefreshToken(tokens.refresh_token);
  }
  
  return client;
}
```

### Security Best Practices

When integrating with ADHD Calendar, follow these security practices:

1. **Store tokens securely**: Never expose API keys or refresh tokens in client-side code
2. **Implement PKCE**: Use PKCE (Proof Key for Code Exchange) for OAuth flows
3. **Validate state parameters**: Prevent CSRF attacks in OAuth callbacks
4. **Use HTTPS**: Always use HTTPS for all API communication
5. **Implement rate limiting**: Respect API rate limits and implement retry mechanisms
6. **Minimize permissions**: Request only the OAuth scopes your application needs

## Testing and Validation

### Sandbox Environment

All integrations should be tested in the sandbox environment before moving to production:

```javascript
// JavaScript SDK Example
const client = new adhd.Client({
  apiKey: 'your-sandbox-api-key',
  environment: 'sandbox'
});
```

### Test Users

The sandbox environment provides test users with pre-configured data:

| Username | Description |
|----------|-------------|
| `test_inattentive` | Test user with inattentive ADHD profile |
| `test_hyperactive` | Test user with hyperactive ADHD profile |
| `test_combined` | Test user with combined ADHD profile |
| `test_calendar_conflict` | Test user with calendar conflicts |

### Testing Tools

The SDK includes tools for testing your integration:

```javascript
// JavaScript SDK Example
const testUtils = adhd.TestUtils;

// Generate test data
const mockProfile = testUtils.generateMotivationProfile({
  type: 'achievement_focused'
});

const mockTasks = testUtils.generateExternalTasks(10, {
  status_distribution: { in_progress: 0.3, to_do: 0.5, done: 0.2 }
});

// Mock API responses for testing
testUtils.mockApiResponse('getUserMotivationProfile', mockProfile);
testUtils.mockApiResponse('getExternalTasks', mockTasks);

// Verify integration correctness
const issues = await testUtils.verifyIntegration({
  components: ['gamification', 'project_tools'],
  testCases: ['profile_update', 'task_sync']
});

if (issues.length > 0) {
  console.error('Integration issues found:', issues);
} else {
  console.log('Integration verification successful!');
}
```

### Certification Process

Before releasing your integration to production, you must complete the certification process:

1. Run the integration verification tests
2. Submit your integration for review in the Developer Portal
3. Address any issues identified during the review
4. Receive certification approval

Certified integrations receive an "ADHD Calendar Certified" badge that can be displayed on your application.

## Additional Resources

- [API Reference Documentation](./epic6_api_reference.md)
- [Sample Integration Code](https://github.com/adhd-calendar/integration-examples)
- [Developer Portal](https://developers.adhd-calendar.example.com)
- [Integration Webinars](https://developers.adhd-calendar.example.com/webinars)
- [Support Forum](https://forum.adhd-calendar.example.com/developers)

For personalized integration support, contact integration-support@adhd-calendar.example.com