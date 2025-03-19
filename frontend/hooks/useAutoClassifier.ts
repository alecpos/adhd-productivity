import { useCallback } from 'react';

import { classifierService } from '../services/classifierService';

interface ClassificationResult {
  category: string;
  confidence: number;
  rules: string[];
}

export function useAutoClassifier() {
  const classifySubmission = useCallback((text: string): ClassificationResult => {
    // Automatically classify the input without user intervention
    const result = classifierService.classifyInput(text);
    
    // If we have high confidence, automatically learn from this submission
    if (result.confidence > 0.7) {
      classifierService.learnFromFeedback(text, result.category);
    }
    
    return result;
  }, []);

  const getRecommendedActions = useCallback((category: string): string[] => {
    switch (category) {
      case 'task':
        return ['Create a new task', 'Set a deadline', 'Add to todo list'];
      case 'calendar':
        return ['Schedule an event', 'Set a reminder', 'Add to calendar'];
      case 'mental_health':
        return ['Track mood', 'Log emotions', 'Set wellness reminder'];
      case 'focus':
        return ['Start focus timer', 'Block distractions', 'Set productivity goal'];
      default:
        return [];
    }
  }, []);

  return {
    classifySubmission,
    getRecommendedActions,
  };
} 