# Frontend App Directory

This directory contains the main application screens and navigation structure for the ADHD Calendar frontend.

## Overview

The app directory is structured using Expo Router, which provides file-based routing for the application. Each file or directory in this folder represents a route in the application, making navigation structure clear and intuitive.

## Directory Structure

- **index.tsx**: Main entry point and home screen
- **(auth)/**: Authentication-related screens
  - **login.tsx**: Login screen
  - **register.tsx**: Registration screen
  - **forgot-password.tsx**: Password recovery screen
- **(tabs)/**: Main tab navigation after authentication
  - **index.tsx**: Tab navigation configuration
  - **dashboard.tsx**: Main dashboard screen
  - **calendar.tsx**: Calendar view
  - **tasks.tsx**: Task management
  - **analytics.tsx**: Productivity analytics
  - **settings.tsx**: User settings
- **_layout.tsx**: Root layout configuration
- **modal/**: Modal screens
  - **help.tsx**: Help modal
  - **notifications.tsx**: Notifications modal

## Key Features

### Home Screen

The home screen provides:
- Quick access to main features
- Overview of today's schedule
- Productivity insights
- Recent activity

### Authentication

Authentication screens handle:
- User login
- New user registration
- Password recovery
- Social authentication

### Tab Navigation

The tab navigation includes:
- Dashboard: Overview of schedule, tasks, and insights
- Calendar: Monthly/weekly/daily calendar views
- Tasks: Task management with ML-powered insights
- Analytics: Productivity pattern visualization
- Settings: User preferences and app configuration

## Implementation Notes

### Routing

The app uses Expo Router for navigation:
- File-based routing simplifies navigation structure
- Deep linking is supported automatically
- Type safety is provided through TypeScript

### State Management

- Redux is used for global state management
- React Context is used for feature-specific state
- Redux Toolkit for efficient Redux implementation
- Zustand for simple UI state

### Styling

- Themed components using @rneui/themed
- Consistent styling with shared theme
- Responsive design for different screen sizes
- Support for light/dark mode

## Usage Example

```typescript
// Example of navigating to the calendar screen
import { router } from 'expo-router';

const navigateToCalendar = () => {
  router.push('/(tabs)/calendar');
};
```

## Adding New Screens

To add a new screen:

1. Create a new file in the appropriate directory
2. Export a React component as the default export
3. The file name will determine the route path
4. Update any necessary navigation configurations

## Documentation

For more details on the frontend implementation, see:
- [Frontend Architecture](../../docs/frontend_architecture.md)
- [Component Guide](../../docs/component_guide.md)
- [State Management](../../docs/state_management.md)
