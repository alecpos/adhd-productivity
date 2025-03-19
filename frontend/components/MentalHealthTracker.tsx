import React, { useState } from 'react';

import { Text, Card, Slider, useTheme, makeStyles } from '@rneui/themed';
import { View } from 'react-native';

import { AnimatedButton } from './ui/AnimatedButton';

interface MentalHealthMetrics {
  anxiety: number;
  mood: number;
  stress: number;
}

export function MentalHealthTracker() {
  const { theme } = useTheme();
  const styles = useStyles();
  const [metrics, setMetrics] = useState<MentalHealthMetrics>({
    anxiety: 5,
    mood: 5,
    stress: 5,
  });

  const handleSave = async () => {
    // TODO: Implement saving metrics to backend
    console.log('Saving mental health metrics:', metrics);
  };

  return (
    <Card containerStyle={styles.container}>
      <Card.Title>Mental Health Tracker</Card.Title>
      <View style={styles.metricsContainer}>
        <View style={styles.metricItem}>
          <Text style={styles.label}>Anxiety Level (1-10)</Text>
          <Slider
            value={metrics.anxiety}
            onValueChange={(value) => setMetrics(prev => ({ ...prev, anxiety: value }))}
            minimumValue={1}
            maximumValue={10}
            step={1}
            thumbStyle={{ backgroundColor: theme.colors.primary }}
            trackStyle={{ height: 4 }}
          />
          <Text style={styles.value}>{metrics.anxiety}</Text>
        </View>

        <View style={styles.metricItem}>
          <Text style={styles.label}>Mood (1-10)</Text>
          <Slider
            value={metrics.mood}
            onValueChange={(value) => setMetrics(prev => ({ ...prev, mood: value }))}
            minimumValue={1}
            maximumValue={10}
            step={1}
            thumbStyle={{ backgroundColor: theme.colors.primary }}
            trackStyle={{ height: 4 }}
          />
          <Text style={styles.value}>{metrics.mood}</Text>
        </View>

        <View style={styles.metricItem}>
          <Text style={styles.label}>Stress Level (1-10)</Text>
          <Slider
            value={metrics.stress}
            onValueChange={(value) => setMetrics(prev => ({ ...prev, stress: value }))}
            minimumValue={1}
            maximumValue={10}
            step={1}
            thumbStyle={{ backgroundColor: theme.colors.primary }}
            trackStyle={{ height: 4 }}
          />
          <Text style={styles.value}>{metrics.stress}</Text>
        </View>
      </View>

      <AnimatedButton
        title="Save Mental Health Log"
        onPress={handleSave}
        scaleOnPress
        containerStyle={styles.button}
      />
    </Card>
  );
}

const useStyles = makeStyles((theme) => ({
  container: {
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    marginBottom: theme.spacing.md,
  },
  metricsContainer: {
    gap: theme.spacing.lg,
    marginBottom: theme.spacing.lg,
  },
  metricItem: {
    marginBottom: theme.spacing.sm,
  },
  label: {
    marginBottom: theme.spacing.xs,
    fontSize: theme.fontSize.md,
    fontWeight: '500',
    color: theme.colors.text,
  },
  value: {
    textAlign: 'center',
    marginTop: theme.spacing.xs,
    fontSize: theme.fontSize.md,
    fontWeight: 'bold',
    color: theme.colors.text,
  },
  button: {
    marginTop: theme.spacing.sm,
    borderRadius: theme.borderRadius.md,
    overflow: 'hidden',
  },
}));