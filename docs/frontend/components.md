# Frontend Components

This document provides a comprehensive overview of the React Native components used in the ADHD Calendar frontend application.

## Component Overview

The ADHD Calendar app uses a component-based architecture built on React Native with Expo. Components are organized into logical groups based on their function within the application.

## Core Components

### TaskCard

The `TaskCard` component displays task information and provides actions for task management.

**Location**: `frontend/components/TaskCard.tsx`

**Props**:
```typescript
interface TaskCardProps {
    task: Task;
    onComplete: () => void;
    onDelete: () => void;
}
```

**Functionality**:
- Displays task title, description, and due date
- Shows task priority and energy requirements
- Provides actions to complete task, delete task, and start focus session
- Integrates with the HyperfocusContext for focus session management

**Usage Example**:
```jsx
<TaskCard
    task={taskObject}
    onComplete={handleTaskComplete}
    onDelete={handleTaskDelete}
/>
```

**Theming**:
The component uses the application's theme system via `makeStyles` and `useTheme` from '@rneui/themed' for consistent styling.

### FocusTimer

The `FocusTimer` component implements a Pomodoro technique timer with configurable work and break durations.

**Location**: `frontend/components/FocusTimer.tsx`

**State Management**:
```typescript
interface TimerState {
  minutes: number;
  seconds: number;
  isRunning: boolean;
  isPaused: boolean;
  isBreak: boolean;
  cyclesCompleted: number;
}

interface TimerSettings {
  workDuration: number;
  shortBreakDuration: number;
  longBreakDuration: number;
  cyclesBeforeLongBreak: number;
}
```

**Functionality**:
- Implements a customizable Pomodoro technique timer
- Manages work sessions and breaks (short and long)
- Provides start/pause/resume/reset controls
- Displays visual progress indicator
- Tracks completed cycles
- Includes configurable settings:
  - Work duration (1-60 minutes)
  - Short break duration (1-30 minutes)
  - Long break duration (5-45 minutes)
  - Number of cycles before long break (2-6)

**Usage Example**:
```jsx
<FocusTimer />
```

**Visual Feedback**:
- Shows the current state (Focus Time or Break Time)
- Displays a progress bar for the current session
- Provides informative messages based on the current state

## ADHD-Specific Components

### ADHDCalendarDashboard

The main dashboard component that provides an ADHD-friendly overview of tasks, events, and energy patterns.

**Location**: `frontend/components/ADHDCalendarDashboard.tsx`

**Functionality**:
- Shows prioritized tasks based on ADHD-specific factors
- Visualizes energy levels throughout the day
- Provides quick actions for task management
- Includes visual cues and reminders

### EnergyLevelTracker

Component for tracking and visualizing user energy levels.

**Location**: `frontend/components/EnergyLevelTracker.tsx`

**Functionality**:
- Allows users to log current energy levels
- Displays historical energy data
- Shows predicted energy patterns
- Provides insights on optimal times for different tasks

## Organizational Structure

Components are organized as follows:

1. **Core Components** (`/components/core/`) - Basic UI building blocks
2. **Feature Components** (`/components/`) - Components tied to specific features
3. **Screen Components** (`/screens/`) - Full screen components that combine other components
4. **Navigation Components** (`/navigation/`) - Components for app navigation

## Styling System

The application uses a consistent styling system based on:

1. A theming provider from '@rneui/themed'
2. Reusable style hooks created with makeStyles
3. Responsive design for different device sizes
4. ADHD-friendly design principles:
   - High contrast options
   - Reduced visual clutter
   - Clear hierarchy and focus
   - Motion sensitivity controls

## Component Best Practices

When creating or modifying components:

1. Use TypeScript interfaces for component props
2. Implement proper error handling
3. Support light and dark themes
4. Consider accessibility needs specific to ADHD users
5. Maintain consistent naming conventions
6. Include PropTypes or TypeScript types for documentation
7. Follow the project's established style patterns

## Related Documentation

- [UI/UX Guidelines](./ui_guidelines.md)
- [Theme Configuration](./theme.md)
- [Accessibility Features](./accessibility.md)
