import React from 'react';
import { SafeAreaView, StyleSheet } from 'react-native';
import { ScheduleOptimizer } from '../components/epic4/ScheduleOptimizer';
import { Stack } from 'expo-router';

export default function ScheduleOptimizerScreen() {
  return (
    <SafeAreaView style={styles.container}>
      <Stack.Screen
        options={{
          title: 'Schedule Optimizer',
          headerShown: true
        }}
      />
      <ScheduleOptimizer />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});
