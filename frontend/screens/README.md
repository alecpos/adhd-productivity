# Screens Directory

This directory contains screen components for the ADHD Calendar frontend application.

## Overview

The screens directory houses the main screens of the application. Each screen represents a complete view that users interact with and is typically associated with a route in the navigation system.

## Screen Categories

### Authentication Screens

- **LoginScreen**: User login screen
- **RegisterScreen**: User registration screen
- **ForgotPasswordScreen**: Password recovery screen
- **VerificationScreen**: Account verification screen

### Main Screens

- **HomeScreen**: Main dashboard/home screen
- **CalendarScreen**: Calendar view screen
- **TaskScreen**: Task management screen
- **TaskDetailScreen**: Individual task detail screen
- **ProfileScreen**: User profile screen
- **SettingsScreen**: Application settings screen

### ML Feature Screens

- **ProductivityPatternScreen**: Productivity pattern visualization and insights
- **TimeEstimationScreen**: Task time estimation screen
- **CommitmentTrackerScreen**: Commitment tracking and management
- **EnergyProfileScreen**: Energy level visualization and insights

### Administrative Screens

- **AdminDashboardScreen**: Admin dashboard screen
- **UserManagementScreen**: User management for administrators
- **AnalyticsScreen**: Analytics and reporting screen

## Screen Structure

Each screen typically includes:

- Screen component file (`.tsx`)
- Screen-specific components (if applicable)
- Screen styles
- Screen tests (`.test.tsx`)

## Screen Organization

Screens are organized hierarchically:

- Root-level screens for main navigation points
- Nested screens for feature-specific flows
- Modal screens for overlay content

## Screen Example

```tsx
import React, { useEffect, useState } from 'react';
import { View, StyleSheet } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { Typography, Container, Button, TaskList } from '../components';
import { useTasks } from '../hooks';
import { Task } from '../types';

const TaskScreen = () => {
  const navigation = useNavigation();
  const { tasks, loading, error, fetchTasks } = useTasks();

  useEffect(() => {
    fetchTasks();
  }, []);

  const handleTaskPress = (task: Task) => {
    navigation.navigate('TaskDetail', { taskId: task.id });
  };

  const handleAddTask = () => {
    navigation.navigate('CreateTask');
  };

  return (
    <Container>
      <Typography variant="h1">Tasks</Typography>

      {loading ? (
        <Spinner />
      ) : error ? (
        <ErrorDisplay message={error} onRetry={fetchTasks} />
      ) : (
        <TaskList
          tasks={tasks}
          onTaskPress={handleTaskPress}
        />
      )}

      <Button
        variant="primary"
        onPress={handleAddTask}
      >
        Add New Task
      </Button>
    </Container>
  );
};

export default TaskScreen;
```

## State Management

Screens typically manage state through:

- Local component state with useState
- Application state with Redux
- Form state with React Hook Form
- Navigation state/params

## Navigation

Screens integrate with the navigation system:

- Access navigation object via useNavigation hook
- Receive route parameters via useRoute hook
- Navigate between screens
- Pass parameters to other screens

## Data Fetching

Screens often fetch data through:

- Custom hooks for data fetching
- API service calls
- Redux actions/thunks
- React Query for cached data

## Development Guidelines

When creating new screens:

1. Follow consistent naming (e.g., `FeatureNameScreen.tsx`)
2. Use appropriate layout components for consistent UX
3. Handle loading, error, and empty states
4. Implement proper navigation flows
5. Follow accessibility guidelines
6. Write tests for all screens
7. Keep business logic in hooks or services

## Related Documentation

- [Navigation System](../docs/navigation.md)
- [Screen Development](../docs/screen_development.md)
- [State Management](../docs/state_management.md)
