import React from 'react';
import { SafeAreaView, StyleSheet } from 'react-native';
import { ProductivityPatternViewer } from '../components/epic1/ProductivityPatternViewer';
import { Stack } from 'expo-router';

export default function ProductivityPatternViewerScreen() {
  return (
    <SafeAreaView style={styles.container}>
      <Stack.Screen 
        options={{ 
          title: 'Productivity Patterns',
          headerShown: true
        }} 
      />
      <ProductivityPatternViewer />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
}); 