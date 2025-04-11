# Hooks Directory

This directory contains custom React hooks for the ADHD Calendar frontend application.

## Overview

The hooks directory houses custom React hooks that encapsulate reusable logic across the application. These hooks follow React best practices and help separate concerns, making components more focused on presentation rather than logic.

## Hook Categories

### Data Fetching Hooks

- **useUser**: Fetches and manages user data
- **useTasks**: Fetches and manages task data
- **useEvents**: Fetches and manages calendar events
- **useCommitments**: Fetches and manages commitment data

### ML-Related Hooks

- **useProductivityPatterns**: Provides productivity pattern data and analysis
- **useTimeEstimation**: Handles time estimation functionality
- **useCircadianProfile**: Provides circadian rhythm and energy level data
- **useTaskRecommendations**: Provides ML-based task recommendations

### Authentication Hooks

- **useAuth**: Manages authentication state and methods
- **useProtectedRoute**: Protects routes based on authentication state
- **usePermissions**: Manages user permissions and access control

### Form Hooks

- **useForm**: Wraps form state and validation
- **useFormField**: Manages individual form field state
- **useFormValidation**: Handles form validation logic

### UI Hooks

- **useTheme**: Provides theme data and functions
- **useBreakpoint**: Handles responsive layout breakpoints
- **useMediaQuery**: Media query functionality for React components
- **useOffline**: Detects and handles offline state

## Hook Structure

Each hook typically:

1. Defines inputs (parameters)
2. Manages internal state
3. Implements side effects with useEffect
4. Returns values and functions
5. Includes TypeScript typing

## Usage Example

```tsx
import React from 'react';
import { View, Text } from 'react-native';
import { useTasks } from '../hooks';
import { TaskList, Spinner, ErrorDisplay } from '../components';

const TaskScreen = () => {
  const {
    tasks,
    loading,
    error,
    fetchTasks,
    addTask,
    updateTask,
    deleteTask
  } = useTasks();

  if (loading) return <Spinner />;
  if (error) return <ErrorDisplay message={error} onRetry={fetchTasks} />;

  return (
    <View>
      <TaskList
        tasks={tasks}
        onUpdate={updateTask}
        onDelete={deleteTask}
      />
      <Button onPress={() => addTask({ title: 'New Task' })}>
        Add Task
      </Button>
    </View>
  );
};
```

## Testing Hooks

Hooks are tested using React Testing Library's `renderHook` function:

```tsx
import { renderHook, act } from '@testing-library/react-hooks';
import { useTasks } from '../hooks';

describe('useTasks', () => {
  test('should fetch tasks on mount', async () => {
    const { result, waitForNextUpdate } = renderHook(() => useTasks());

    expect(result.current.loading).toBe(true);

    await waitForNextUpdate();

    expect(result.current.loading).toBe(false);
    expect(result.current.tasks).toHaveLength(3);
  });
});
```

## Development Guidelines

When creating new hooks:

1. Focus on a single responsibility
2. Use descriptive names that indicate functionality
3. Properly handle loading, error, and success states
4. Include TypeScript types for parameters and return values
5. Document parameters and return values
6. Write tests for all hooks
7. Handle cleanup and memory management with useEffect

## Related Documentation

- [React Hooks Documentation](https://reactjs.org/docs/hooks-intro.html)
- [Custom Hooks Guide](../docs/custom_hooks.md)
- [Data Fetching Patterns](../docs/data_fetching.md)
