import React, { useState } from 'react';
import { SafeAreaView, StyleSheet, Text, View, ScrollView, TouchableOpacity } from 'react-native';
import { ThemeProvider, Button } from '@rneui/themed';

// Import our components
import { ProductivityPatternViewer } from './components/epic1/ProductivityPatternViewer';
import { CircadianRhythmView } from './components/epic1/CircadianRhythmView';
import { DurationEstimator } from './components/epic2/DurationEstimator';
import { CommitmentTracker } from './components/epic3/CommitmentTracker';
import { ScheduleOptimizer } from './components/epic4/ScheduleOptimizer';
import { ExplainableAI } from './components/epic5/ExplainableAI';
import { AdaptiveUI } from './components/epic6/AdaptiveUI';
import { ADHDCalendarDashboard } from './components/ADHDCalendarDashboard';

// Create a simple theme
const theme = {
  colors: {
    primary: '#4782DA',
    secondary: '#47A6DA',
    background: '#FFFFFF',
    surface: '#F5F5F5',
    error: '#DA4747',
    text: '#333333',
    grey5: '#E0E0E0',
    grey3: '#AAAAAA',
    grey1: '#666666',
  },
  // Add any other theme elements needed
};

// Component mapping for navigation
const COMPONENTS = {
  'Dashboard': ADHDCalendarDashboard,
  'Productivity Patterns': ProductivityPatternViewer,
  'Energy Patterns': CircadianRhythmView,
  'Duration Estimator': DurationEstimator,
  'Commitment Tracker': CommitmentTracker,
  'Schedule Optimizer': ScheduleOptimizer,
  'AI Explanations': ExplainableAI,
  'UI Preferences': AdaptiveUI,
};

// Main App that doesn't use Expo Router
export default function SimpleTestApp() {
  const [activeComponent, setActiveComponent] = useState<keyof typeof COMPONENTS>('Dashboard');
  
  // Render the currently selected component
  const ActiveComponent = COMPONENTS[activeComponent];
  
  return (
    <ThemeProvider theme={theme}>
      <SafeAreaView style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.headerTitle}>ADHD Calendar</Text>
          <Text style={styles.headerSubtitle}>Component Testing</Text>
        </View>
        
        <ScrollView horizontal style={styles.navigation} showsHorizontalScrollIndicator={false}>
          {Object.keys(COMPONENTS).map((componentName) => (
            <TouchableOpacity
              key={componentName}
              style={[
                styles.navButton,
                componentName === activeComponent && styles.activeNavButton
              ]}
              onPress={() => setActiveComponent(componentName as keyof typeof COMPONENTS)}
            >
              <Text 
                style={[
                  styles.navButtonText,
                  componentName === activeComponent && styles.activeNavButtonText
                ]}
              >
                {componentName}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
        
        <ScrollView style={styles.componentContainer}>
          <ActiveComponent />
        </ScrollView>
        
        <View style={styles.footer}>
          <Button
            title="Back to Dashboard"
            type="clear"
            disabled={activeComponent === 'Dashboard'}
            onPress={() => setActiveComponent('Dashboard')}
          />
        </View>
      </SafeAreaView>
    </ThemeProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#4782DA',
    padding: 15,
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: 'white',
  },
  headerSubtitle: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.8)',
  },
  navigation: {
    backgroundColor: 'white',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  navButton: {
    paddingHorizontal: 15,
    paddingVertical: 8,
    marginHorizontal: 5,
    borderRadius: 20,
    backgroundColor: '#f0f0f0',
  },
  activeNavButton: {
    backgroundColor: '#4782DA',
  },
  navButtonText: {
    fontSize: 14,
    color: '#666666',
  },
  activeNavButtonText: {
    color: 'white',
    fontWeight: 'bold',
  },
  componentContainer: {
    flex: 1,
  },
  footer: {
    padding: 10,
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
    backgroundColor: 'white',
    alignItems: 'center',
  },
}); 