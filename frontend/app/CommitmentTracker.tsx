import React from 'react';
import { SafeAreaView, StyleSheet } from 'react-native';
import { CommitmentTracker } from '../components/epic3/CommitmentTracker';
import { Stack } from 'expo-router';

export default function CommitmentTrackerScreen() {
  return (
    <SafeAreaView style={styles.container}>
      <Stack.Screen 
        options={{ 
          title: 'Commitment Tracker',
          headerShown: true
        }} 
      />
      <CommitmentTracker />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
}); 