import React from 'react';
import { SafeAreaView, StyleSheet } from 'react-native';
import { AdaptiveUI } from '../components/epic6/AdaptiveUI';
import { Stack } from 'expo-router';

export default function AdaptiveUIScreen() {
  return (
    <SafeAreaView style={styles.container}>
      <Stack.Screen 
        options={{ 
          title: 'UI Preferences',
          headerShown: true
        }} 
      />
      <AdaptiveUI />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
}); 