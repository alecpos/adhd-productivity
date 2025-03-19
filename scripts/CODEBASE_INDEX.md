# Codebase Structure

## Frontend Components

### Calendar Management
- `Calendar.tsx`: Base calendar component for displaying and managing events
- `CalendarManager.tsx`: Higher-order component managing calendar state and interactions

### Task Management
- `TaskCreate.tsx`: Modal form for creating and editing tasks
- `TaskCard.tsx`: Display component for individual tasks
- `TaskList.tsx`: Container component for displaying multiple tasks

### State Management
- `store/slices/taskSlice.ts`: Redux slice managing task state
  - Full CRUD operations
  - Task interfaces and types
  - Loading and error states

### Supporting Components
- `BlockScheduler.tsx`: Component for block-based scheduling
- `SchedulingBlock.tsx`: Individual scheduling block component
- `SchedulingContainer.tsx`: Container for scheduling blocks
- `AISchedulingAssistant.tsx`: AI-powered scheduling assistance
- `PatternVisualizer.tsx`: Visualization of scheduling patterns

### Health & Productivity
- `EnergyLevelTracker.tsx`: Track and manage energy levels
- `FocusTimer.tsx`: Pomodoro-style focus timer
- `MentalHealthTracker.tsx`: Mental health tracking component

## Core Features

### Task Management
- Create, read, update, and delete tasks
- Task prioritization and scheduling
- Redux-based state management
- Task synchronization with calendar

### Calendar Integration
- Calendar view and management
- Task scheduling and visualization
- Block-based scheduling
- AI-assisted scheduling recommendations

### Health & Productivity
- Energy level tracking
- Focus timer
- Mental health monitoring
- Pattern analysis and visualization

## Testing
- Component unit tests
- Redux store tests (needs improvement)
- Integration tests between components
- Calendar sync testing

## Future Improvements
1. Increase test coverage for Redux store
2. Add integration tests for calendar-task synchronization
3. Enhance documentation with JSDoc comments
4. Implement additional health tracking features
