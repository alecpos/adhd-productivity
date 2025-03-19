import React, { useEffect, useState } from 'react';

import { View, Text, StyleSheet } from 'react-native';

import { classifierService } from '../services/classifierService';

import { PatternVisualizer } from './PatternVisualizer';

interface Pattern {
  category: string;
  text: string;
  rules?: string[];
  examples?: string[];
}

export const UserInputClassifier: React.FC = () => {
  const [patterns, setPatterns] = useState<Pattern[]>([]);

  useEffect(() => {
    const loadPatterns = async () => {
      try {
        const loadedPatterns = await classifierService.getPatterns();
        const transformedPatterns = loadedPatterns.map(pattern => ({
          category: pattern.category,
          text: pattern.pattern || '',
          rules: pattern.rules,
          examples: pattern.examples,
        }));
        setPatterns(transformedPatterns);
      } catch (error) {
        console.error('Failed to load patterns:', error);
      }
    };

    loadPatterns();
  }, []);

  return (
    <View style={styles.container}>
      <PatternVisualizer patterns={patterns} />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
}); 