# Types Directory

This directory contains TypeScript type definitions for the ADHD Calendar frontend application.

## Overview

The types directory houses TypeScript type definitions, interfaces, and type utilities that are used throughout the application. These types provide a strong type system to enhance development experience, prevent errors, and improve code maintainability.

## Type Categories

### Domain Types

- **user.types.ts**: User and authentication related types
- **task.types.ts**: Task and todo related types
- **calendar.types.ts**: Calendar and event related types
- **notification.types.ts**: Notification related types

### ML-Related Types

- **productivity.types.ts**: Productivity pattern related types
- **timeEstimation.types.ts**: Time estimation related types
- **circadian.types.ts**: Circadian rhythm and energy level types
- **commitment.types.ts**: Commitment tracking related types

### API Types

- **api.types.ts**: API request and response types
- **error.types.ts**: Error handling types
- **http.types.ts**: HTTP related types

### UI Types

- **navigation.types.ts**: Navigation related types
- **theme.types.ts**: Theme and styling related types
- **component.types.ts**: Common component prop types
- **form.types.ts**: Form related types

### Utility Types

- **common.types.ts**: Common utility types
- **enums.ts**: Enumeration types
- **utils.types.ts**: Type utility functions

## Type Definitions

Type definitions follow these patterns:

### Interfaces

```typescript
// user.types.ts example
export interface User {
  id: string;
  email: string;
  displayName: string;
  profileImageUrl?: string;
  createdAt: string;
  updatedAt: string;
}

export interface UserProfile extends User {
  bio?: string;
  preferences: UserPreferences;
  stats: UserStats;
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'system';
  notificationsEnabled: boolean;
  calendarView: 'day' | 'week' | 'month';
  // ...other preferences
}

export interface UserStats {
  taskCompletionRate: number;
  averageTaskDuration: number;
  // ...other stats
}
```

### Type Aliases

```typescript
// task.types.ts example
export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent';

export type TaskStatus = 'pending' | 'in_progress' | 'completed' | 'canceled' | 'deferred';

export type Task = {
  id: string;
  title: string;
  description?: string;
  priority: TaskPriority;
  status: TaskStatus;
  dueDate?: string;
  estimatedDuration?: number; // in minutes
  actualDuration?: number; // in minutes
  tags: string[];
  userId: string;
  createdAt: string;
  updatedAt: string;
};

export type TaskCreateInput = Omit<Task, 'id' | 'createdAt' | 'updatedAt' | 'actualDuration'>;

export type TaskUpdateInput = Partial<TaskCreateInput>;
```

### Enums

```typescript
// enums.ts example
export enum AuthProvider {
  EMAIL = 'email',
  GOOGLE = 'google',
  APPLE = 'apple',
}

export enum NotificationType {
  TASK_DUE = 'task_due',
  TASK_REMINDER = 'task_reminder',
  SYSTEM = 'system',
  COMMITMENT = 'commitment',
}

export enum TimeEstimationConfidence {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
}
```

### Utility Types

```typescript
// utils.types.ts example
/**
 * Makes all properties of T nullable
 */
export type Nullable<T> = { [P in keyof T]: T[P] | null };

/**
 * Extracts the success response type from an API response
 */
export type ApiSuccessResponse<T> = {
  data: T;
  status: 'success';
  message?: string;
};

/**
 * Extracts the error response type from an API response
 */
export type ApiErrorResponse = {
  status: 'error';
  message: string;
  code?: string;
};

/**
 * Combines success and error response types
 */
export type ApiResponse<T> = ApiSuccessResponse<T> | ApiErrorResponse;

/**
 * Utility type for pagination results
 */
export type PaginatedResult<T> = {
  items: T[];
  totalItems: number;
  page: number;
  pageSize: number;
  totalPages: number;
  hasNextPage: boolean;
  hasPreviousPage: boolean;
};
```

## Usage Example

```typescript
// Component using types
import React, { useState, useEffect } from 'react';
import { View, Text } from 'react-native';
import { Task, TaskStatus } from '../types/task.types';
import { fetchTasks } from '../services/task.service';

interface TaskListProps {
  userId: string;
  status?: TaskStatus;
}

const TaskList: React.FC<TaskListProps> = ({ userId, status }) => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadTasks = async () => {
      try {
        const taskData = await fetchTasks(userId, status);
        setTasks(taskData);
      } catch (error) {
        console.error('Failed to fetch tasks:', error);
      } finally {
        setLoading(false);
      }
    };

    loadTasks();
  }, [userId, status]);

  return (
    <View>
      {tasks.map(task => (
        <Text key={task.id}>{task.title}</Text>
      ))}
    </View>
  );
};
```

## Type Organization

Types are organized to:

- Keep related types in the same file
- Group by domain concept rather than technical concept
- Follow consistent naming conventions
- Provide extensive documentation

## Best Practices

When creating or modifying types:

1. Use interfaces for objects that will be extended
2. Use type aliases for unions, intersections, and simple object types
3. Use descriptive names that indicate purpose
4. Document complex types with JSDoc comments
5. Keep types focused on specific domains
6. Use composition over inheritance
7. Export all public types
8. Use utility types to avoid repetition

## Related Documentation

- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [TypeScript Style Guide](../docs/typescript_style_guide.md)
- [API Type System](../docs/api_type_system.md) 