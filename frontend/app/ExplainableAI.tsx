import React from 'react';
import { SafeAreaView, StyleSheet } from 'react-native';
import { ExplainableAI } from '../components/epic5/ExplainableAI';
import { Stack } from 'expo-router';

export default function ExplainableAIScreen() {
  return (
    <SafeAreaView style={styles.container}>
      <Stack.Screen 
        options={{ 
          title: 'AI Explanations',
          headerShown: true
        }} 
      />
      <ExplainableAI />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
}); 