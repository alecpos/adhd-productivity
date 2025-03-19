# Navigation Directory

This directory contains navigation configuration and components for the ADHD Calendar frontend application.

## Overview

The navigation directory houses the navigation structure, routes, and navigation-related components for the application. It defines how users move between different screens and the overall information architecture of the app.

## Navigation Structure

The application uses a multi-level navigation structure:

- **Root Navigator**: Top-level navigation container
- **Authentication Navigator**: Handles authentication flows
- **Main Navigator**: Post-authentication navigation
  - **Tab Navigator**: Bottom tab navigation for main sections
  - **Stack Navigators**: Stack-based navigation within sections
  - **Modal Navigators**: Modal presentation for overlays

## Key Files

- **index.tsx**: Main navigation entry point
- **RootNavigator.tsx**: Root navigation container
- **AuthNavigator.tsx**: Authentication-related navigation
- **MainNavigator.tsx**: Main application navigation
- **TabNavigator.tsx**: Bottom tab navigation
- **CalendarNavigator.tsx**: Calendar section navigation
- **TasksNavigator.tsx**: Tasks section navigation
- **SettingsNavigator.tsx**: Settings section navigation
- **types.ts**: Navigation type definitions

## Navigation Configuration

Each navigator is configured with:

- Screen definitions and components
- Navigation options (headers, animations, etc.)
- Default screen settings
- Transition styles

## Route Naming Convention

Routes follow a consistent naming convention:

- Authentication routes: `Auth.Login`, `Auth.Register`, etc.
- Tab routes: `Main.Home`, `Main.Calendar`, `Main.Tasks`, etc.
- Stack routes: `Calendar.Month`, `Calendar.Day`, `Tasks.List`, `Tasks.Detail`, etc.
- Modal routes: `Modal.CreateTask`, `Modal.Settings`, etc.

## Usage Example

```tsx
import React from 'react';
import { useNavigation } from '@react-navigation/native';
import { Button } from 'react-native';
import { StackNavigationProp } from '@react-navigation/stack';
import { RootStackParamList } from './types';

// Define navigation prop type
type TaskScreenNavigationProp = StackNavigationProp<
  RootStackParamList,
  'Tasks.List'
>;

const TaskListScreen = () => {
  // Get navigation object
  const navigation = useNavigation<TaskScreenNavigationProp>();

  // Navigate to task detail screen
  const navigateToTaskDetail = (taskId: string) => {
    navigation.navigate('Tasks.Detail', { taskId });
  };

  // Navigate to create task modal
  const navigateToCreateTask = () => {
    navigation.navigate('Modal.CreateTask');
  };

  return (
    <View>
      <Text>Task List</Text>
      <Button 
        title="View Task Detail" 
        onPress={() => navigateToTaskDetail('task-123')} 
      />
      <Button 
        title="Create New Task" 
        onPress={navigateToCreateTask} 
      />
    </View>
  );
};
```

## Type Safety

Navigation is fully typed using TypeScript:

- Parameter lists for each route
- Navigation prop types
- Route typing for each navigator

```tsx
// types.ts example
export type RootStackParamList = {
  Auth: NavigatorScreenParams<AuthStackParamList>;
  Main: NavigatorScreenParams<MainTabParamList>;
  'Modal.CreateTask': undefined;
  'Modal.Settings': undefined;
};

export type AuthStackParamList = {
  'Auth.Login': undefined;
  'Auth.Register': undefined;
  'Auth.ForgotPassword': undefined;
};

export type MainTabParamList = {
  'Main.Home': undefined;
  'Main.Calendar': NavigatorScreenParams<CalendarStackParamList>;
  'Main.Tasks': NavigatorScreenParams<TasksStackParamList>;
  'Main.Profile': undefined;
};

export type TasksStackParamList = {
  'Tasks.List': undefined;
  'Tasks.Detail': { taskId: string };
  'Tasks.Edit': { taskId: string };
};
```

## Deep Linking

Deep linking configuration is defined to support external links:

- URL configuration
- Path mapping to screens
- Parameter extraction from URLs

## Authentication Flow

The navigation system handles authentication flows:

- Conditional rendering based on authentication state
- Protected routes
- Authentication redirects

## Development Guidelines

When extending the navigation:

1. Follow the established naming conventions
2. Update the navigation types
3. Keep navigators focused on specific sections
4. Use appropriate navigator types (stack, tab, drawer)
5. Configure proper headers and transitions
6. Update deep linking configuration
7. Consider accessibility

## Related Documentation

- [React Navigation Documentation](https://reactnavigation.org/docs/getting-started)
- [Navigation Patterns](../docs/navigation_patterns.md)
- [Deep Linking Guide](../docs/deep_linking.md) 