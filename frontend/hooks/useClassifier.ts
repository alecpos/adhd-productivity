import { useState, useEffect } from 'react';

import AsyncStorage from '@react-native-async-storage/async-storage';

export interface Pattern {
  category: string;
  text: string;
  confidence: number;
  rules?: string[];
  examples?: string[];
}

export function useClassifier() {
  const [patterns, setPatterns] = useState<Pattern[]>([]);

  useEffect(() => {
    loadPatterns();
  }, []);

  const loadPatterns = async () => {
    try {
      const storedPatterns = await AsyncStorage.getItem('learned_patterns');
      if (storedPatterns) {
        setPatterns(JSON.parse(storedPatterns));
      }
    } catch (error) {
      console.error('Error loading patterns:', error);
    }
  };

  const savePattern = async (pattern: Pattern) => {
    try {
      const updatedPatterns = [...patterns, pattern];
      await AsyncStorage.setItem('learned_patterns', JSON.stringify(updatedPatterns));
      setPatterns(updatedPatterns);
    } catch (error) {
      console.error('Error saving pattern:', error);
    }
  };

  const clearPatterns = async () => {
    try {
      await AsyncStorage.removeItem('learned_patterns');
      setPatterns([]);
    } catch (error) {
      console.error('Error clearing patterns:', error);
    }
  };

  return {
    patterns,
    savePattern,
    clearPatterns,
  };
} 