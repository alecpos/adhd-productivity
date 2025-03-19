import React from 'react';
import { SafeAreaView, StyleSheet } from 'react-native';
import { DurationEstimator } from '../components/epic2/DurationEstimator';
import { Stack } from 'expo-router';

export default function DurationEstimatorScreen() {
  return (
    <SafeAreaView style={styles.container}>
      <Stack.Screen 
        options={{ 
          title: 'Duration Estimator',
          headerShown: true
        }} 
      />
      <DurationEstimator />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
}); 