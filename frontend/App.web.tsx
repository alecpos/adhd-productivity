// Web-specific entry point that doesn't use problematic native modules
import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { ThemeProvider, createTheme, Button } from '@rneui/themed';

import { NotificationProvider } from './contexts/NotificationContext';
import { ProductivityPatternViewer } from './components/epic1/ProductivityPatternViewer';
import { CircadianRhythmView } from './components/epic1/CircadianRhythmView';

// Create a theme
const theme = createTheme({
  lightColors: {
    primary: '#4782DA',
    secondary: '#47A6DA',
    background: '#FFFFFF',
    error: '#DA4747',
    grey5: '#E0E0E0',
    grey3: '#AAAAAA',
    grey1: '#666666',
  },
  darkColors: {
    primary: '#4782DA',
    secondary: '#47A6DA',
    background: '#121212',
    error: '#DA4747',
    grey5: '#303030',
    grey3: '#5C5C5C',
    grey1: '#8E8E8E',
  },
  mode: 'light',
});

// Ensure theme colors are defined
const themeColors = {
  primary: theme.lightColors?.primary || '#4782DA',
  secondary: theme.lightColors?.secondary || '#47A6DA',
  background: theme.lightColors?.background || '#FFFFFF',
  grey1: theme.lightColors?.grey1 || '#666666',
};

// List of available components
const epicComponents = [
  { name: 'Productivity Pattern Viewer', component: ProductivityPatternViewer },
  { name: 'Circadian Rhythm View', component: CircadianRhythmView },
  // Add other components here
];

export default function App(): JSX.Element {
  const [selectedComponent, setSelectedComponent] = useState<string | null>(null);

  // Render the selected component or show a list of components
  const renderContent = () => {
    if (selectedComponent) {
      const ComponentToRender = epicComponents.find(c => c.name === selectedComponent)?.component;

      return (
        <View style={styles.componentContainer}>
          <Button
            title="← Back to Components"
            type="clear"
            onPress={() => setSelectedComponent(null)}
            containerStyle={styles.backButton}
          />

          {ComponentToRender ? <ComponentToRender /> : <Text>Component not found</Text>}
        </View>
      );
    }

    // Component selector
    return (
      <ScrollView style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.headerText}>ADHD Calendar Web Viewer</Text>
          <Text style={styles.subHeaderText}>
            Select a component to view:
          </Text>
        </View>

        <View style={styles.componentList}>
          {epicComponents.map(comp => (
            <TouchableOpacity
              key={comp.name}
              style={styles.componentCard}
              onPress={() => setSelectedComponent(comp.name)}
            >
              <Text style={styles.componentName}>{comp.name}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </ScrollView>
    );
  };

  return (
    <SafeAreaProvider>
      <ThemeProvider theme={theme}>
        <NotificationProvider>
          {renderContent()}
        </NotificationProvider>
      </ThemeProvider>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    padding: 20,
    marginVertical: 20,
    backgroundColor: themeColors.background,
    borderRadius: 8,
    margin: 10,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  headerText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: themeColors.primary,
    marginBottom: 10,
    textAlign: 'center',
  },
  subHeaderText: {
    fontSize: 16,
    color: themeColors.grey1,
    textAlign: 'center',
  },
  componentList: {
    padding: 10,
  },
  componentCard: {
    backgroundColor: themeColors.background,
    borderRadius: 8,
    padding: 20,
    marginVertical: 8,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  componentName: {
    fontSize: 18,
    color: themeColors.primary,
    fontWeight: '500',
  },
  componentContainer: {
    flex: 1,
    backgroundColor: themeColors.background,
  },
  backButton: {
    padding: 10,
    margin: 10,
  },
});
