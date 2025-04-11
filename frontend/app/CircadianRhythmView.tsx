import React from 'react';
import { SafeAreaView, StyleSheet } from 'react-native';
import { CircadianRhythmView } from '../components/epic1/CircadianRhythmView';
import { Stack } from 'expo-router';

export default function CircadianRhythmViewScreen() {
  return (
    <SafeAreaView style={styles.container}>
      <Stack.Screen
        options={{
          title: 'Energy Patterns',
          headerShown: true
        }}
      />
      <CircadianRhythmView />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});
