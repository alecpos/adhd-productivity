import React from 'react';

import { makeStyles } from '@rneui/themed';
import { View, Text, ScrollView } from 'react-native';

interface Pattern {
  category: string;
  text: string;
  rules?: string[];
  examples?: string[];
}

interface PatternVisualizerProps {
  patterns: Pattern[];
}

const useStyles = makeStyles((theme) => ({
  container: {
    flex: 1,
    padding: theme.spacing.md,
  },
  title: {
    fontSize: theme.fontSize.lg,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: theme.spacing.md,
  },
  chartContainer: {
    marginBottom: theme.spacing.lg,
  },
  barContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: theme.spacing.sm,
  },
  labelContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: '100%',
  },
  barLabel: {
    fontSize: theme.fontSize.md,
    color: theme.colors.text,
  },
  barCount: {
    fontSize: theme.fontSize.sm,
    color: theme.colors.grey3,
  },
  barWrapper: {
    flex: 1,
    height: 10,
    backgroundColor: theme.colors.grey5,
    borderRadius: theme.borderRadius.sm,
    overflow: 'hidden',
  },
  bar: {
    height: '100%',
    backgroundColor: theme.colors.primary,
  },
  listContainer: {
    marginTop: theme.spacing.lg,
  },
  subtitle: {
    fontSize: theme.fontSize.md,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: theme.spacing.md,
  },
  patternItem: {
    marginBottom: theme.spacing.md,
  },
  category: {
    fontSize: theme.fontSize.sm,
    fontWeight: 'bold',
    color: theme.colors.secondary,
  },
  pattern: {
    fontSize: theme.fontSize.sm,
    color: theme.colors.text,
  },
  rulesContainer: {
    marginTop: theme.spacing.sm,
    paddingTop: theme.spacing.sm,
    borderTopWidth: 1,
    borderTopColor: theme.colors.grey4,
  },
  rulesTitle: {
    fontSize: theme.fontSize.xs,
    fontWeight: '500',
    color: theme.colors.grey3,
    marginBottom: theme.spacing.xs,
  },
  ruleText: {
    fontSize: theme.fontSize.xs,
    color: theme.colors.grey3,
    marginLeft: theme.spacing.xs,
    marginBottom: theme.spacing.xs,
  },
}));

export const PatternVisualizer: React.FC<PatternVisualizerProps> = ({ patterns }) => {
  const styles = useStyles();
  const categoryData = patterns.reduce((acc, pattern) => {
    acc[pattern.category] = (acc[pattern.category] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const maxCount = Math.max(...Object.values(categoryData));

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Pattern Distribution</Text>
      <View style={styles.chartContainer}>
        {Object.entries(categoryData).map(([category, count]) => (
          <View key={category} style={styles.barContainer}>
            <View style={styles.labelContainer}>
              <Text style={styles.barLabel}>{category}</Text>
              <Text style={styles.barCount}>{count}</Text>
            </View>
            <View style={styles.barWrapper}>
              <View
                style={[
                  styles.bar,
                  { width: `${(count / maxCount) * 100}%` }
                ]}
              />
            </View>
          </View>
        ))}
      </View>
      <View style={styles.listContainer}>
        <Text style={styles.subtitle}>Learned Patterns</Text>
        {patterns.map((pattern, index) => (
          <View key={index} style={styles.patternItem}>
            <Text style={styles.category}>{pattern.category}</Text>
            <Text style={styles.pattern}>{pattern.text}</Text>
            {pattern.rules && pattern.rules.length > 0 && (
              <View style={styles.rulesContainer}>
                <Text style={styles.rulesTitle}>Rules:</Text>
                {pattern.rules.map((rule, ruleIndex) => (
                  <Text key={ruleIndex} style={styles.ruleText}>• {rule}</Text>
                ))}
              </View>
            )}
          </View>
        ))}
      </View>
    </ScrollView>
  );
};
