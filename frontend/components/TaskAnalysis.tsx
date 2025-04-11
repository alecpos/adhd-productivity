import React, { useState } from 'react';

import { View, Text, ActivityIndicator, StyleSheet } from 'react-native';

import { Button } from '../app/components/ui/Button';
import api from '../app/services/api';

interface TaskAnalysisProps {
  taskDescription: string;
  taskType: string;
}

export const TaskAnalysis: React.FC<TaskAnalysisProps> = ({ taskDescription, taskType }) => {
  const [analysis, setAnalysis] = useState<any>(null);
  const [strategies, setStrategies] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyzeTask = async () => {
    setLoading(true);
    setError(null);
    try {
      const [analysisResult, strategiesResult] = await Promise.all([
        api.post('/nlp/analyze-task', { task_description: taskDescription }),
        api.post('/nlp/focus-strategies', { task_type: taskType })
      ]);

      setAnalysis(analysisResult.data);
      setStrategies(strategiesResult.data);
    } catch (err) {
      setError('Failed to analyze task. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#0000ff" />
        <Text>Analyzing task...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.container}>
        <Text style={styles.error}>{error}</Text>
        <Button onPress={analyzeTask} title="Retry Analysis" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {!analysis ? (
        <Button onPress={analyzeTask} title="Analyze Task" />
      ) : (
        <>
          <View style={styles.section}>
            <Text style={styles.heading}>Task Analysis</Text>
            <Text>{analysis.analysis}</Text>
          </View>

          {strategies.length > 0 && (
            <View style={styles.section}>
              <Text style={styles.heading}>Recommended Focus Strategies</Text>
              {strategies.map((strategy, index) => (
                <Text key={index} style={styles.strategy}>
                  • {strategy}
                </Text>
              ))}
            </View>
          )}
        </>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 16,
    backgroundColor: '#fff',
    borderRadius: 8,
    marginVertical: 8,
  },
  section: {
    marginBottom: 16,
  },
  heading: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  strategy: {
    marginBottom: 4,
    lineHeight: 20,
  },
  error: {
    color: 'red',
    marginBottom: 8,
  },
});
