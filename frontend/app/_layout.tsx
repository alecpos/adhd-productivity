import React from 'react';

import { useFonts } from 'expo-font';
import { Stack } from 'expo-router';
import * as SplashScreen from 'expo-splash-screen';
import { ThemeProvider, createTheme } from '@rneui/themed';
import { ActivityIndicator, View, StyleSheet } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import { NotificationProvider } from '../contexts/NotificationContext';

// Create a theme
const theme = createTheme({
  lightColors: {
    primary: '#4782DA',
    secondary: '#47A6DA',
    background: '#FFFFFF',
    error: '#DA4747',
    grey5: '#E0E0E0',
    grey3: '#AAAAAA',
    grey1: '#666666',
  },
  darkColors: {
    primary: '#4782DA',
    secondary: '#47A6DA',
    background: '#121212',
    error: '#DA4747',
    grey5: '#303030',
    grey3: '#5C5C5C',
    grey1: '#8E8E8E',
  },
  mode: 'light',
});

// Prevent splash screen from auto-hiding
void SplashScreen.preventAutoHideAsync();

function LoadingScreen(): JSX.Element {
  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <ActivityIndicator size="large" color={theme.lightColors?.primary} />
    </View>
  );
}

export default function RootLayout(): JSX.Element | null {
  const [fontsLoaded] = useFonts({
    'SpaceMono-Regular': require('../assets/fonts/SpaceMono-Regular.ttf'),
  });

  // Hide splash screen when fonts are loaded
  React.useEffect(() => {
    if (fontsLoaded) {
      void SplashScreen.hideAsync();
    }
  }, [fontsLoaded]);

  // Show loading screen while fonts are loading
  if (!fontsLoaded) {
    return <LoadingScreen />;
  }

  // Provider setup
  return (
    <SafeAreaProvider>
      <ThemeProvider theme={theme}>
        <NotificationProvider>
          <Stack 
            screenOptions={{
              headerShown: true,
              headerTitleAlign: 'center',
            }}
          />
        </NotificationProvider>
      </ThemeProvider>
    </SafeAreaProvider>
  );
}

// Unused styles - keeping for future use
const _styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});
