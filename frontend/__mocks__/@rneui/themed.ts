import React from 'react';

import { View } from 'react-native';

import type { StyleProp, ViewProps, ViewStyle } from 'react-native';

// Define the Theme type since we can't import it directly
interface ThemeColors {
  primary: string;
  background: string;
  black: string;
  grey4: string;
  grey5: string;
}

export interface Theme {
  colors: ThemeColors;
  mode: 'light' | 'dark';
}

// RNE Card Props
export interface CardProps extends ViewProps {
  containerStyle?: StyleProp<ViewStyle>;
  wrapperStyle?: StyleProp<ViewStyle>;
  theme?: Theme;
  children?: React.ReactNode;
  testID: string;
  variant?: 'elevated' | 'outlined' | 'filled';
  size?: 'small' | 'medium' | 'large';
  noPadding?: boolean;
  fullWidth?: boolean;
}

// Mock the RNECard component
export const Card = React.forwardRef<View, CardProps>((props, ref) => {
  const { containerStyle, children, testID, ...rest } = props;
  return React.createElement(View, {
    ref,
    style: containerStyle,
    testID,
    ...rest,
  }, children);
});

Card.displayName = 'Card';

// Create Title subcomponent
const CardTitle = React.forwardRef<View, ViewProps>((props, ref) => {
  return React.createElement(View, { ref, ...props });
});

CardTitle.displayName = 'Card.Title';

// Attach Title to Card
Object.defineProperty(Card, 'Title', {
  value: CardTitle,
  configurable: true,
  enumerable: true,
});

const defaultTheme: Theme = {
  colors: {
    primary: '#2089dc',
    background: '#ffffff',
    black: '#242424',
    grey4: '#bdc6cf',
    grey5: '#e1e8ee',
  },
  mode: 'light',
};

export const ThemeContext = React.createContext<{ theme: Theme }>({ theme: defaultTheme });

export const makeStyles = <T extends Record<string, StyleProp<ViewStyle>>>(
  styles: ((theme: Theme) => T) | T
): (() => T) => {
  return () => {
    const { theme } = useTheme();
    if (typeof styles === 'function') {
      return styles(theme);
    }
    return styles;
  };
};

export const useTheme = (): { theme: Theme } => {
  const context = React.useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

interface ThemeProviderProps {
  theme?: Theme;
  children: React.ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ theme = defaultTheme, children }) => {
  const value = React.useMemo(() => ({ theme }), [theme]);
  return React.createElement(ThemeContext.Provider, { value }, children);
};

export const createTheme = (config: Partial<Theme>): Theme => ({
  ...defaultTheme,
  ...config,
});

// Mock the RNECard component as both default and named export
export { Card as default };
