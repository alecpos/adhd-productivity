# Components Directory

This directory contains React Native components for the ADHD Calendar frontend application.

## Overview

The components directory houses reusable UI components that are used throughout the application. These components follow React and React Native best practices and are designed to be modular, reusable, and maintainable.

## Component Categories

### Core Components

- **Button**: Custom button components with different styles and states
- **Input**: Text input components with validation
- **Card**: Container components for content
- **Typography**: Text components with consistent styling
- **Spinner**: Loading indicators
- **Modal**: Modal dialog components

### Layout Components

- **Container**: Basic layout containers
- **Grid**: Grid layout components
- **FlexBox**: Flexbox layout components
- **Spacer**: Components for adding consistent spacing

### Form Components

- **Form**: Form container components
- **FormField**: Field components with labels and validation
- **Checkbox**: Checkbox input components
- **RadioButton**: Radio button components
- **Dropdown**: Dropdown/select components
- **DatePicker**: Date selection components

### Navigation Components

- **Header**: Header/app bar components
- **TabBar**: Tab navigation components
- **Drawer**: Drawer menu components
- **NavigationLink**: Navigation link components

### ML-Related Components

- **ProductivityChart**: Productivity pattern visualization
- **EnergyLevelIndicator**: Energy level visualization
- **TimeEstimationDisplay**: Time estimation visualization
- **CommitmentList**: Commitment tracking components

## Component Structure

Each component typically consists of:

- Component file (`.tsx`)
- Styles file (if applicable)
- Types file (if complex)
- Test file (`.test.tsx`)
- Index file for exporting

## Usage Example

```tsx
import React from 'react';
import { Container, Card, Typography, Button } from '../components';

const TaskScreen = () => {
  return (
    <Container>
      <Card>
        <Typography variant="h1">Task Details</Typography>
        <Typography variant="body">Description of the task...</Typography>
        <Button variant="primary" onPress={() => console.log('Button pressed')}>
          Complete Task
        </Button>
      </Card>
    </Container>
  );
};

export default TaskScreen;
```

## Component Documentation

Components should be documented with:

- Purpose and usage description
- Props documentation with types and defaults
- Example usage
- Variations and states
- Accessibility considerations

## Theming

Components use the application's theme system:

- Theme-aware styling with consistent colors, typography, and spacing
- Support for light and dark modes
- Responsive design for different screen sizes
- Accessibility features built-in

## Testing

Components include unit and snapshot tests:

- Test basic rendering
- Test prop variations
- Test user interactions
- Test accessibility

## Development Guidelines

When creating new components:

1. Focus on reusability and composability
2. Follow the project's design system
3. Include proper TypeScript typing
4. Ensure responsive behavior
5. Consider accessibility requirements
6. Write tests for all components
7. Document props and usage examples

## Related Documentation

- [Design System Guide](../docs/design_system.md)
- [Component Development](../docs/component_development.md)
- [Accessibility Guidelines](../docs/accessibility.md) 