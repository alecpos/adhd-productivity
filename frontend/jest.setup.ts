// Polyfills
import { TextEncoder, TextDecoder } from 'util';

import type { createElement } from 'react';

import type { Theme } from '@rneui/themed';
import type { View, ViewStyle } from 'react-native';

// Mock React Native components
jest.mock('react-native', () => ({
  View: 'View',
  Text: 'Text',
  TouchableOpacity: 'TouchableOpacity',
  StyleSheet: {
    create: (styles: Record<string, unknown>) => styles,
  },
}));

// Mock @rneui/themed components
jest.mock('@rneui/themed', () => ({
  ...jest.requireActual('@rneui/themed'),
  Card: 'Card',
  ThemeProvider: ({ children }: { children: React.ReactNode }) => children,
}));

interface Global {
  TextEncoder: typeof TextEncoder;
  TextDecoder: typeof TextDecoder;
  createNodeMock: (element: ElementMock) => MockRef | null;
}

interface ElementMock {
  type: string | (() => JSX.Element);
}

interface MockRef {
  scrollTo: jest.Mock;
  scrollToEnd: jest.Mock;
  measure: jest.Mock;
  measureInWindow: jest.Mock;
  measureLayout: jest.Mock;
  setNativeProps: jest.Mock;
  focus: jest.Mock;
  blur: jest.Mock;
  children: unknown[];
}

declare const global: Global;

global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;

// Mock fetch
// eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
const fetchMock = require('jest-fetch-mock');
// eslint-disable-next-line @typescript-eslint/no-unsafe-member-access, @typescript-eslint/no-unsafe-call
fetchMock.enableMocks();

// Mock AsyncStorage
jest.mock('@react-native-async-storage/async-storage', () => ({
  setItem: jest.fn(() => Promise.resolve()),
  getItem: jest.fn(() => Promise.resolve()),
  removeItem: jest.fn(() => Promise.resolve()),
  clear: jest.fn(() => Promise.resolve()),
  getAllKeys: jest.fn(() => Promise.resolve([])),
  multiGet: jest.fn(() => Promise.resolve([])),
  multiSet: jest.fn(() => Promise.resolve()),
  multiRemove: jest.fn(() => Promise.resolve()),
}));

// Mock Expo Router
jest.mock('expo-router', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    back: jest.fn(),
  }),
  useLocalSearchParams: () => ({}),
  Link: 'Link',
}));

// Mock Expo Vector Icons
jest.mock('@expo/vector-icons', () => ({
  FontAwesome: 'FontAwesome',
  MaterialIcons: 'MaterialIcons',
  Ionicons: 'Ionicons',
}));

jest.mock('@expo/vector-icons/FontAwesome', () => 'FontAwesome');

// Mock react-native-reanimated
jest.mock('react-native-reanimated', () => {
  const RN = jest.requireActual<{ View: typeof View }>('react-native');
  return {
    View: RN.View,
    createAnimatedComponent: (component: React.ComponentType<ViewStyle>) => component,
  };
});

// Mock axios
jest.mock('axios', () => ({
  create: jest.fn(() => ({
    get: jest.fn(() => Promise.resolve({ data: {} })),
    post: jest.fn(() => Promise.resolve({ data: {} })),
    put: jest.fn(() => Promise.resolve({ data: {} })),
    delete: jest.fn(() => Promise.resolve({ data: {} })),
    interceptors: {
      request: { use: jest.fn(), eject: jest.fn() },
      response: { use: jest.fn(), eject: jest.fn() },
    },
  })),
}));

// Mock Expo Font
jest.mock('expo-font', () => ({
  useFonts: jest.fn(() => [true, null]),
  loadAsync: jest.fn(() => Promise.resolve()),
}));

// Mock Expo Splash Screen
jest.mock('expo-splash-screen', () => ({
  preventAutoHideAsync: jest.fn(() => Promise.resolve()),
  hideAsync: jest.fn(() => Promise.resolve()),
}));

// Mock @rneui/themed
jest.mock('@rneui/themed', () => {
  const mockTheme: Theme = {
    spacing: { xs: 4, sm: 8, md: 16, lg: 24, xl: 32 },
    mode: 'light',
    colors: {
      primary: '#2089dc',
      background: '#ffffff',
      black: '#242424',
      grey4: '#bdc6cf',
      grey5: '#e1e8ee',
    }
  };

  const React = jest.requireActual('react');
  const RN = jest.requireActual('react-native');

  const withTheme = <P extends object>(Component: React.ComponentType<P>, name: string): React.FC<P & { theme?: Theme }> => {
    const ThemedComponent: React.FC<P & { theme?: Theme }> = (props) => {
      return React.createElement(Component, {
        ...props,
        theme: mockTheme,
      });
    };
    ThemedComponent.displayName = `Themed${name}`;
    return ThemedComponent;
  };

  const CardBase: React.FC<{ style?: ViewStyle; children?: React.ReactNode }> = (props) => React.createElement(RN.View, props);
  const CardDivider: React.FC<{ style?: ViewStyle }> = (props) => React.createElement(RN.View, props);
  const CardImage: React.FC<{ source: { uri: string }; style?: ViewStyle }> = (props) => React.createElement(RN.Image, props);
  const CardTitle: React.FC<{ style?: ViewStyle; children?: React.ReactNode }> = (props) => React.createElement(RN.Text, props);

  const ThemedCard = Object.assign(withTheme(CardBase, 'Card'), {
    Divider: withTheme(CardDivider, 'CardDivider'),
    Image: withTheme(CardImage, 'CardImage'),
    Title: withTheme(CardTitle, 'CardTitle'),
    FeaturedTitle: withTheme(CardTitle, 'CardFeaturedTitle'),
    FeaturedSubtitle: withTheme(CardTitle, 'CardFeaturedSubtitle'),
  });

  return {
    Card: ThemedCard,
    ThemeProvider: ({ children, theme }: { children: React.ReactNode; theme?: Theme }) => React.createElement(React.Fragment, null, children),
    makeStyles: (styles: ((theme: Theme) => Record<string, ViewStyle>) | Record<string, ViewStyle>) => () => {
      if (typeof styles === 'function') {
        return styles(mockTheme);
      }
      return styles;
    },
    useTheme: () => ({ theme: mockTheme }),
    createTheme: (config: Partial<Theme>) => ({ ...mockTheme, ...config }),
    withTheme,
  };
});

// Configure React Test Renderer to handle refs
global.createNodeMock = (element: ElementMock) => {
  if (element.type === 'ScrollView' ||
      element.type === 'Text' ||
      element.type === 'View' ||
      element.type === 'RCTScrollView' ||
      element.type === 'RNGestureHandlerButton' ||
      typeof element.type === 'function') {
    return {
      scrollTo: jest.fn(),
      scrollToEnd: jest.fn(),
      measure: jest.fn(),
      measureInWindow: jest.fn(),
      measureLayout: jest.fn(),
      setNativeProps: jest.fn(),
      focus: jest.fn(),
      blur: jest.fn(),
      children: [],
    };
  }
  return null;
};
