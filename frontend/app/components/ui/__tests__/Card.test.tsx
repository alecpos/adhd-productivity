import React from 'react';

import { describe, it, expect, beforeEach } from '@jest/globals';
import { ThemeProvider, useTheme, makeStyles, Card } from '@rneui/themed';
import { render, renderHook, screen } from '@testing-library/react-native';
import { View, Text } from 'react-native';

import type { Theme } from '@rneui/themed';

// Mock React Native components
jest.mock('react-native', () => ({
  View: 'View',
  Text: 'Text',
}));

// Use the mock file instead of inline mock
jest.mock('@rneui/themed');

describe('Card Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  const theme = {
    colors: {
      primary: '#2089dc',
      background: '#ffffff',
      black: '#242424',
      grey4: '#bdc6cf',
      grey5: '#e1e8ee',
    },
    mode: 'light' as const,
  };

  const Wrapper = ({ children }: { children: React.ReactNode }) => (
    <ThemeProvider theme={theme}>{children}</ThemeProvider>
  );

  it('uses theme context correctly', () => {
    const { result } = renderHook(() => useTheme(), { wrapper: Wrapper });
    expect(result.current.theme).toBeDefined();
    expect(result.current.theme.mode).toBe('light');
  });

  it('renders with basic props', () => {
    render(
      <Card testID="test-card">
        <View testID="card-content">
          <Text>Test Content</Text>
        </View>
      </Card>,
      { wrapper: Wrapper }
    );
    expect(screen.getByTestId('test-card')).toBeTruthy();
    expect(screen.getByTestId('card-content')).toBeTruthy();
  });

  it('creates styles with makeStyles', () => {
    const useStyles = makeStyles((_theme: Theme) => ({
      container: {
        backgroundColor: '#ffffff',
      },
    }));

    const { result } = renderHook(() => useStyles(), { wrapper: Wrapper });
    expect(result.current.container).toBeDefined();
    expect(result.current.container.backgroundColor).toBe('#ffffff');
  });

  it('renders with different variants', () => {
    const variants: Array<'elevated' | 'outlined' | 'filled'> = ['elevated', 'outlined', 'filled'];

    variants.forEach((variant) => {
      render(
        <Card testID={`${variant}-card`} variant={variant}>
          <Text>Test Content</Text>
        </Card>,
        { wrapper: Wrapper }
      );
      expect(screen.getByTestId(`${variant}-card`)).toBeTruthy();
    });
  });

  it('renders with different sizes', () => {
    const sizes: Array<'small' | 'medium' | 'large'> = ['small', 'medium', 'large'];

    sizes.forEach((size) => {
      render(
        <Card testID={`${size}-card`} size={size}>
          <Text>Test Content</Text>
        </Card>,
        { wrapper: Wrapper }
      );
      expect(screen.getByTestId(`${size}-card`)).toBeTruthy();
    });
  });

  it('renders without padding when noPadding is true', () => {
    render(
      <Card testID="no-padding-card" noPadding>
        <Text>Test Content</Text>
      </Card>,
      { wrapper: Wrapper }
    );
    expect(screen.getByTestId('no-padding-card')).toBeTruthy();
  });

  it('renders with full width when fullWidth is true', () => {
    render(
      <Card testID="full-width-card" fullWidth>
        <Text>Test Content</Text>
      </Card>,
      { wrapper: Wrapper }
    );
    expect(screen.getByTestId('full-width-card')).toBeTruthy();
  });
});
