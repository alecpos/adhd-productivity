import React from 'react';

import { configureStore } from '@reduxjs/toolkit';
import { ThemeProvider } from '@rneui/themed';
import { render } from '@testing-library/react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { Provider } from 'react-redux';

import taskReducer from '@/app/store/slices/taskSlice';
import { ADHDSettingsProvider } from '@/contexts/ADHDSettingsContext';
import { AuthProvider } from '@/contexts/AuthContext';
import { CalendarProvider } from '@/contexts/CalendarContext';
import { GamificationProvider } from '@/contexts/GamificationContext';
import { HyperfocusProvider } from '@/contexts/HyperfocusContext';
import { MentalHealthProvider } from '@/contexts/MentalHealthContext';
import { TaskProvider } from '@/contexts/TaskContext';

// Create a mock store
const createTestStore = () => {
  return configureStore({
    reducer: {
      tasks: taskReducer
    }
  });
};

const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  const store = createTestStore();

  return (
    <Provider store={store}>
      <SafeAreaProvider>
        <ThemeProvider>
          <AuthProvider>
            <TaskProvider>
              <ADHDSettingsProvider>
                <CalendarProvider>
                  <GamificationProvider>
                    <HyperfocusProvider>
                      <MentalHealthProvider>
                        {children}
                      </MentalHealthProvider>
                    </HyperfocusProvider>
                  </GamificationProvider>
                </CalendarProvider>
              </ADHDSettingsProvider>
            </TaskProvider>
          </AuthProvider>
        </ThemeProvider>
      </SafeAreaProvider>
    </Provider>
  );
};

const customRender = (ui: React.ReactElement, options = {}) =>
  render(ui, { wrapper: AllTheProviders, ...options });

// re-export everything
export * from '@testing-library/react-native';

// override render method
export { customRender as render };
