import React from 'react';

import { ThemeProvider } from '@rneui/themed';
import { SafeAreaProvider } from 'react-native-safe-area-context';


import { useADHDSettings } from '@/contexts/ADHDSettingsContext';
import { useMentalHealth } from '@/contexts/MentalHealthContext';

import { render } from '../../../test-utils';
import ADHDDashboard from '../ADHDDashboard';

import type { CreateThemeOptions } from '@rneui/themed';


// Mock the hooks
jest.mock('@/contexts/ADHDSettingsContext', () => ({
  ...jest.requireActual('@/contexts/ADHDSettingsContext'),
  useADHDSettings: jest.fn()
}));

jest.mock('@/contexts/MentalHealthContext', () => ({
  ...jest.requireActual('@/contexts/MentalHealthContext'),
  useMentalHealth: jest.fn()
}));

// Mock React Native components and APIs
jest.mock('react-native', () => {
  const RN = jest.requireActual('react-native');
  return {
    ...RN,
    StyleSheet: {
      create: (styles: any) => styles,
    },
    View: 'View',
    Text: 'Text',
    ScrollView: 'ScrollView',
  };
});

// Mock LoadingSpinner component
jest.mock('../../../components/ui/LoadingSpinner', () => 'LoadingSpinner');

// Mock theme
const mockTheme: CreateThemeOptions = {
  lightColors: {
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
  darkColors: {
    primary: '#2089dc',
    secondary: '#ca71eb',
    background: '#000000',
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
  mode: 'light'
};

const renderWithProviders = (ui: React.ReactElement) => {
  return render(
    <SafeAreaProvider>
      <ThemeProvider theme={mockTheme}>
        {ui}
      </ThemeProvider>
    </SafeAreaProvider>
  );
};

describe('ADHDDashboard', () => {
  beforeEach(() => {
    // Mock the hook implementations
    (useADHDSettings as jest.Mock).mockReturnValue({
      profile: {},
      metrics: {
        focusScores: { daily: 8.5 },
        taskCompletion: { onTime: 0.85 },
      },
      loading: false,
      error: null,
      logDistraction: jest.fn(),
      logFocusSession: jest.fn(),
      getRecommendations: jest.fn(),
      generateDailyPlan: jest.fn(),
    });

    (useMentalHealth as jest.Mock).mockReturnValue({
      stats: {
        mood_average: 7.5,
        streak: 5,
        recent_moods: [],
      },
      loading: false,
      error: null,
      logEnergyLevel: jest.fn(),
      getStats: jest.fn(),
    });
  });

  it('renders correctly', () => {
    const { getByTestId } = renderWithProviders(<ADHDDashboard />);
    expect(getByTestId('adhd-dashboard')).toBeTruthy();
  });

  it('renders without crashing', () => {
    const { getByText } = renderWithProviders(<ADHDDashboard />);
    expect(getByText('Quick Actions')).toBeTruthy();
  });

  it('displays focus insights correctly', () => {
    const { getByText } = renderWithProviders(<ADHDDashboard />);
    expect(getByText('8.5')).toBeTruthy();
    expect(getByText('85%')).toBeTruthy();
  });

  it('handles energy level updates', () => {
    const mockLogEnergyLevel = jest.fn();
    (useMentalHealth as jest.Mock).mockReturnValue({
      stats: { mood_average: 7.5, streak: 5 },
      loading: false,
      error: null,
      logEnergyLevel: mockLogEnergyLevel,
      getStats: jest.fn(),
    });

    const { getByText } = renderWithProviders(<ADHDDashboard />);
    const energyValue = getByText('5');
    expect(energyValue).toBeTruthy();
  });
});
