import React from 'react';
import { SafeAreaView, StyleSheet } from 'react-native';
import { ADHDCalendarDashboard } from '../components/ADHDCalendarDashboard';

export default function HomePage() {
  return (
    <SafeAreaView style={styles.container}>
      <ADHDCalendarDashboard />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});
