# Utils Directory

This directory contains utility functions and helpers for the ADHD Calendar frontend application.

## Overview

The utils directory houses reusable utility functions and helper modules that are used throughout the application. These utilities provide common functionality, reduce code duplication, and help maintain consistency across the codebase.

## Utility Categories

### Date and Time Utilities

- **dateUtils.ts**: Date formatting, manipulation, and calculation functions
- **timeUtils.ts**: Time-related utilities and conversions
- **calendarUtils.ts**: Calendar-specific helpers for date ranges and events

### Data Manipulation

- **arrayUtils.ts**: Array manipulation and transformation functions
- **objectUtils.ts**: Object manipulation utilities
- **formatUtils.ts**: Data formatting helpers
- **validationUtils.ts**: Data validation functions

### API and Networking

- **apiUtils.ts**: API request helpers and error handling
- **cacheUtils.ts**: Data caching utilities
- **networkUtils.ts**: Network status and connectivity helpers

### Storage Utilities

- **storageUtils.ts**: Local storage and secure storage utilities
- **prefUtils.ts**: User preferences management

### Device and Platform

- **deviceUtils.ts**: Device information and capabilities
- **platformUtils.ts**: Platform-specific utilities
- **dimensionUtils.ts**: Screen dimensions and responsive utilities

### UI Helpers

- **animationUtils.ts**: Animation utility functions
- **colorUtils.ts**: Color manipulation and conversion
- **styleUtils.ts**: Dynamic styling helpers

### ML-Related Utilities

- **productivityUtils.ts**: Productivity pattern calculation helpers
- **timeEstimationUtils.ts**: Time estimation utilities
- **circadianUtils.ts**: Circadian rhythm and energy level helpers

## Common Patterns

### Pure Functions

Most utilities are implemented as pure functions:

```typescript
// arrayUtils.ts example
/**
 * Groups array items by a key extraction function
 * @param array Array to group
 * @param keyFn Function to extract the key from each item
 * @returns Object with keys as group names and values as arrays of items
 */
export function groupBy<T, K extends string | number | symbol>(
  array: T[],
  keyFn: (item: T) => K
): Record<K, T[]> {
  return array.reduce((result, item) => {
    const key = keyFn(item);
    (result[key] = result[key] || []).push(item);
    return result;
  }, {} as Record<K, T[]>);
}
```

### Utility Classes

Some complex utilities are implemented as classes:

```typescript
// cacheUtils.ts example
/**
 * Simple in-memory cache with TTL support
 */
export class MemoryCache {
  private cache: Record<string, { value: any; expires: number }> = {};

  /**
   * Sets a value in the cache with optional TTL
   * @param key Cache key
   * @param value Value to store
   * @param ttl TTL in milliseconds (default: 5 minutes)
   */
  set(key: string, value: any, ttl: number = 5 * 60 * 1000): void {
    this.cache[key] = {
      value,
      expires: Date.now() + ttl
    };
  }

  /**
   * Gets a value from the cache if not expired
   * @param key Cache key
   * @returns Cached value or undefined if not found or expired
   */
  get<T>(key: string): T | undefined {
    const item = this.cache[key];
    if (!item) return undefined;
    if (item.expires < Date.now()) {
      delete this.cache[key];
      return undefined;
    }
    return item.value as T;
  }

  // Other methods: clear, has, delete, etc.
}
```

### Hooks

Many utilities are exposed as custom hooks:

```typescript
// useDebounce.ts example
import { useState, useEffect } from 'react';

/**
 * A hook that debounces a value
 * @param value Value to debounce
 * @param delay Delay in milliseconds
 * @returns Debounced value
 */
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(timer);
    };
  }, [value, delay]);

  return debouncedValue;
}
```

## Usage Example

```typescript
// Using array utilities
import { groupBy, sortBy } from '../utils/arrayUtils';

const tasks = [
  { id: 1, title: 'Task 1', category: 'work' },
  { id: 2, title: 'Task 2', category: 'personal' },
  { id: 3, title: 'Task 3', category: 'work' }
];

// Group tasks by category
const tasksByCategory = groupBy(tasks, task => task.category);
// Result: { work: [task1, task3], personal: [task2] }

// Sort tasks by title
const sortedTasks = sortBy(tasks, task => task.title);
// Result: [task1, task2, task3] sorted alphabetically

// Using date utilities
import { formatDate, getWeekRange } from '../utils/dateUtils';

const today = new Date();
const formattedDate = formatDate(today, 'MM/dd/yyyy');
const { startDate, endDate } = getWeekRange(today);
```

## Testing Utilities

Utilities are thoroughly tested with unit tests:

```typescript
// dateUtils.test.ts example
import { formatDate, getWeekRange } from '../dateUtils';

describe('dateUtils', () => {
  describe('formatDate', () => {
    it('should format date correctly', () => {
      const date = new Date(2023, 0, 15); // Jan 15, 2023
      expect(formatDate(date, 'MM/dd/yyyy')).toBe('01/15/2023');
    });
  });

  describe('getWeekRange', () => {
    it('should return correct week range', () => {
      const date = new Date(2023, 0, 18); // Wed, Jan 18, 2023
      const { startDate, endDate } = getWeekRange(date);
      expect(startDate.getDate()).toBe(15); // Sun, Jan 15
      expect(endDate.getDate()).toBe(21); // Sat, Jan 21
    });
  });
});
```

## Development Guidelines

When adding or modifying utilities:

1. Keep functions focused on a single responsibility
2. Use descriptive names that indicate functionality
3. Add TypeScript type definitions for all parameters and return values
4. Document functions with JSDoc comments
5. Write unit tests for all utilities
6. Consider edge cases and error handling
7. Optimize for performance when appropriate

## Related Documentation

- [Utility Functions Guide](../docs/utility_functions.md)
- [Date and Time Handling](../docs/date_time_handling.md)
- [Custom Hooks](../docs/custom_hooks.md) 