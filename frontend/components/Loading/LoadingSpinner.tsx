import React from 'react';

import { Text, useTheme } from '@rneui/themed';
import { View, ActivityIndicator, StyleSheet } from 'react-native';

interface LoadingSpinnerProps {
  fullScreen?: boolean;
  text?: string;
  size?: 'small' | 'large';
}

export function LoadingSpinner({
  fullScreen = false,
  text = 'Loading...',
  size = 'large'
}: LoadingSpinnerProps) {
  const { theme } = useTheme();

  if (fullScreen) {
    return (
      <View style={[styles.fullScreen, { backgroundColor: theme.colors.background }]}>
        <ActivityIndicator size={size} color={theme.colors.primary} />
        {text && <Text style={[styles.text, { color: theme.colors.grey2 }]}>{text}</Text>}
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <ActivityIndicator size={size} color={theme.colors.primary} />
      {text && <Text style={[styles.text, { color: theme.colors.grey2 }]}>{text}</Text>}
    </View>
  );
}

const styles = StyleSheet.create({
  fullScreen: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  container: {
    padding: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  text: {
    marginTop: 10,
    fontSize: 16,
  },
});
