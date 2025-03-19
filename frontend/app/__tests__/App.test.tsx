import React from 'react';

import { configureStore } from '@reduxjs/toolkit';
import { ThemeProvider } from '@rneui/themed';
import { render, screen } from '@testing-library/react-native';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { Provider } from 'react-redux';

import { ADHDSettingsProvider } from '@/contexts/ADHDSettingsContext';
import { AuthProvider } from '@/contexts/AuthContext';
import { CalendarProvider } from '@/contexts/CalendarContext';
import { GamificationProvider } from '@/contexts/GamificationContext';
import { HyperfocusProvider } from '@/contexts/HyperfocusContext';
import { MentalHealthProvider } from '@/contexts/MentalHealthContext';
import { TaskProvider } from '@/contexts/TaskContext';

import RootLayout from '../_layout';
import ToastProvider from '../components/ui/ToastProvider';
import taskReducer from '../store/slices/taskSlice';

// Mock all the external modules
jest.mock('react-native', () => ({
  ActivityIndicator: 'ActivityIndicator',
  View: 'View',
  Text: 'Text',
  ScrollView: 'ScrollView',
  AccessibilityInfo: {
    announceForAccessibility: jest.fn(),
  }
}));

jest.mock('expo-router', () => ({
  Stack: () => 'Stack',
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    back: jest.fn(),
  }),
}));

jest.mock('react-native-safe-area-context', () => ({
  SafeAreaProvider: ({ children }: { children: React.ReactNode }) => children,
  SafeAreaView: ({ children }: { children: React.ReactNode }) => children,
}));

jest.mock('react-native-gesture-handler', () => ({
  GestureHandlerRootView: ({ children }: { children: React.ReactNode }) => children,
}));

jest.mock('expo-font', () => ({
  useFonts: () => [true],
}));

jest.mock('expo-splash-screen', () => ({
  preventAutoHideAsync: jest.fn(),
  hideAsync: jest.fn(),
}));

jest.mock('@expo/vector-icons/FontAwesome', () => ({
  font: {},
}));

jest.mock('../app/theme', () => ({
  theme: {
    mode: 'light',
    colors: {
      primary: '#2089dc',
      secondary: '#ca71eb',
      background: '#ffffff',
      white: '#ffffff',
      black: '#242424',
      grey0: '#393e42',
      grey1: '#43484d',
      grey2: '#5e6977',
      grey3: '#86939e',
      grey4: '#bdc6cf',
      grey5: '#e1e8ee',
      greyOutline: '#bbb',
      searchBg: '#303337',
      success: '#52c41a',
      error: '#ff190c',
      warning: '#faad14',
      disabled: 'hsl(208, 8%, 90%)',
    },
    spacing: {
      xs: 4,
      sm: 8,
      md: 16,
      lg: 24,
      xl: 32,
    },
  },
}));

// Create a mock store
const createTestStore = () => {
  return configureStore({
    reducer: {
      tasks: taskReducer
    }
  });
};

const renderWithProviders = (ui: React.ReactElement) => {
  const store = createTestStore();
  return render(
    <Provider store={store}>
      <GestureHandlerRootView style={{ flex: 1 }}>
        <SafeAreaProvider>
          <ThemeProvider theme={{ mode: 'light' }}>
            <AuthProvider>
              <TaskProvider>
                <ADHDSettingsProvider>
                  <CalendarProvider>
                    <GamificationProvider>
                      <HyperfocusProvider>
                        <MentalHealthProvider>
                          <ToastProvider>
                            {ui}
                          </ToastProvider>
                        </MentalHealthProvider>
                      </HyperfocusProvider>
                    </GamificationProvider>
                  </CalendarProvider>
                </ADHDSettingsProvider>
              </TaskProvider>
            </AuthProvider>
          </ThemeProvider>
        </SafeAreaProvider>
      </GestureHandlerRootView>
    </Provider>
  );
};

describe('App', () => {
  it('renders without crashing', () => {
    renderWithProviders(<RootLayout />);
    expect(screen.getByTestId('app-root')).toBeTruthy();
  });
});
