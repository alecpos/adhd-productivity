# Theme Directory

This directory contains theming and styling configurations for the ADHD Calendar frontend application.

## Overview

The theme directory houses the application's design system, including theme definitions, color palettes, typography, spacing, and other styling constants. It provides a centralized approach to maintaining a consistent visual language throughout the application.

## Directory Structure

- **index.ts**: Main theme export
- **colors.ts**: Color definitions and palettes
- **typography.ts**: Typography styles and font definitions
- **spacing.ts**: Spacing constants and layout guidelines
- **shadows.ts**: Shadow styles for elevation
- **breakpoints.ts**: Responsive breakpoints
- **components/**: Component-specific theme definitions
- **hooks/**: Theme-related hooks (e.g., useTheme)
- **utils/**: Theme utility functions

## Theme System

The application implements a comprehensive theme system that supports:

- Light and dark mode
- Consistent styling across components
- Responsive design
- Accessibility features
- Custom user preferences

## Colors

The color system includes:

- Primary colors (brand colors)
- Secondary colors
- Neutral colors (grays)
- Semantic colors (success, error, warning, info)
- Background colors
- Text colors
- Accessible contrast ratios

```typescript
// colors.ts example
export const colors = {
  primary: {
    light: '#6200EE',
    main: '#3700B3',
    dark: '#1A00A3',
    contrast: '#FFFFFF'
  },
  secondary: {
    light: '#03DAC6',
    main: '#018786',
    dark: '#016868',
    contrast: '#000000'
  },
  error: {
    light: '#FF5252',
    main: '#B00020',
    dark: '#790000',
    contrast: '#FFFFFF'
  },
  success: {
    light: '#4CAF50',
    main: '#2E7D32',
    dark: '#1B5E20',
    contrast: '#FFFFFF'
  },
  grey: {
    50: '#FAFAFA',
    100: '#F5F5F5',
    200: '#EEEEEE',
    300: '#E0E0E0',
    400: '#BDBDBD',
    500: '#9E9E9E',
    600: '#757575',
    700: '#616161',
    800: '#424242',
    900: '#212121'
  },
  text: {
    primary: 'rgba(0, 0, 0, 0.87)',
    secondary: 'rgba(0, 0, 0, 0.6)',
    disabled: 'rgba(0, 0, 0, 0.38)',
    hint: 'rgba(0, 0, 0, 0.38)'
  },
  background: {
    default: '#FFFFFF',
    paper: '#F5F5F5',
    card: '#FFFFFF'
  }
};

export const darkColors = {
  // Dark mode color definitions
  // ...
};
```

## Typography

Typography definitions include:

- Font families
- Font weights
- Font sizes
- Line heights
- Letter spacing
- Text styles for different components

```typescript
// typography.ts example
export const typography = {
  fontFamily: {
    primary: 'Roboto',
    secondary: 'Open Sans',
    monospace: 'Roboto Mono'
  },
  fontWeight: {
    light: '300',
    regular: '400',
    medium: '500',
    bold: '700'
  },
  fontSize: {
    xs: 12,
    sm: 14,
    md: 16,
    lg: 18,
    xl: 20,
    '2xl': 24,
    '3xl': 30,
    '4xl': 36,
    '5xl': 48
  },
  lineHeight: {
    tight: 1.2,
    normal: 1.5,
    relaxed: 1.75,
    loose: 2
  },
  styles: {
    h1: {
      fontFamily: 'Roboto',
      fontWeight: '700',
      fontSize: 48,
      lineHeight: 1.2
    },
    h2: {
      // ...
    },
    // Additional text styles
  }
};
```

## Spacing

Spacing constants provide consistent layout values:

```typescript
// spacing.ts example
export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  '2xl': 48,
  '3xl': 64,
  '4xl': 96
};
```

## Component Theming

Component-specific theme definitions:

```typescript
// components/button.ts example
import { colors, typography, spacing } from '../';

export const buttonTheme = {
  primary: {
    backgroundColor: colors.primary.main,
    color: colors.primary.contrast,
    padding: `${spacing.sm}px ${spacing.md}px`,
    fontSize: typography.fontSize.md,
    fontWeight: typography.fontWeight.medium,
    borderRadius: 4
  },
  secondary: {
    backgroundColor: colors.secondary.main,
    color: colors.secondary.contrast,
    // ...
  },
  // Additional button variants
};
```

## Theme Usage

Using the theme in components:

```tsx
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useTheme } from '../theme';

const MyComponent = () => {
  const theme = useTheme();
  
  return (
    <View style={styles.container}>
      <Text style={[styles.text, { color: theme.colors.text.primary }]}>
        Themed Text
      </Text>
      <View 
        style={[
          styles.card, 
          { 
            backgroundColor: theme.colors.background.card,
            padding: theme.spacing.md
          }
        ]}
      >
        <Text style={{ ...theme.typography.styles.h2 }}>
          Card Title
        </Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  text: {
    // Base styles
  },
  card: {
    borderRadius: 8,
    // Base styles
  }
});
```

## Dark Mode Support

The theme provides dark mode implementation:

```tsx
// ThemeProvider in app root
import React, { useState, useEffect } from 'react';
import { Appearance } from 'react-native';
import { ThemeProvider } from './theme';

const App = () => {
  const [colorScheme, setColorScheme] = useState(Appearance.getColorScheme());
  
  useEffect(() => {
    const subscription = Appearance.addChangeListener(({ colorScheme }) => {
      setColorScheme(colorScheme);
    });
    
    return () => subscription.remove();
  }, []);
  
  return (
    <ThemeProvider theme={colorScheme === 'dark' ? 'dark' : 'light'}>
      {/* App content */}
    </ThemeProvider>
  );
};
```

## Development Guidelines

When working with the theme:

1. Always use theme values rather than hardcoded styles
2. Extend the theme when adding new design elements
3. Ensure color combinations meet accessibility guidelines
4. Test designs in both light and dark modes
5. Consider responsive design using theme breakpoints
6. Document new theme additions

## Related Documentation

- [Design System](../docs/design_system.md)
- [Styling Guide](../docs/styling_guide.md)
- [Accessibility](../docs/accessibility.md)
- [Component Theming](../docs/component_theming.md) 