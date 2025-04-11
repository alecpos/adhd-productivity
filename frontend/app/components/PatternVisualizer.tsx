import React from 'react';

import { makeStyles } from '@rneui/themed';
import { View, Text, ScrollView } from 'react-native';

import { useClassifier } from '../../hooks/useClassifier';

import type { Pattern } from '../../hooks/useClassifier';

export default function PatternVisualizer() {
  const { patterns } = useClassifier();
  const styles = useStyles();

  const categoryCounts = React.useMemo(() => {
    const counts: { [key: string]: number } = {};
    patterns.forEach((pattern: Pattern) => {
      counts[pattern.category] = (counts[pattern.category] || 0) + 1;
    });
    return counts;
  }, [patterns]);

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Learned Patterns</Text>

      <View style={styles.statsContainer}>
        {Object.entries(categoryCounts).map(([category, count]) => (
          <View key={category} style={styles.statItem}>
            <Text style={styles.statCategory}>{category}</Text>
            <Text style={styles.statCount}>{count}</Text>
          </View>
        ))}
      </View>

      <View style={styles.patternList}>
        {patterns.map((pattern: Pattern, index: number) => (
          <View key={index} style={styles.patternItem}>
            <Text style={styles.category}>{pattern.category}</Text>
            <Text style={styles.text}>{pattern.text}</Text>
            <Text style={styles.confidence}>
              Confidence: {(pattern.confidence * 100).toFixed(1)}%
            </Text>
            {pattern.rules && pattern.rules.length > 0 && (
              <View style={styles.rulesContainer}>
                <Text style={styles.rulesTitle}>Rules:</Text>
                {pattern.rules.map((rule: string, ruleIndex: number) => (
                  <Text key={ruleIndex} style={styles.rule}>
                    • {rule}
                  </Text>
                ))}
              </View>
            )}
          </View>
        ))}
      </View>
    </ScrollView>
  );
}

const useStyles = makeStyles((theme) => ({
  container: {
    flex: 1,
  },
  title: {
    fontSize: theme.fontSize.xl,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: theme.spacing.lg,
    padding: theme.spacing.md,
  },
  statsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: theme.spacing.sm,
    padding: theme.spacing.md,
    marginBottom: theme.spacing.lg,
  },
  statItem: {
    backgroundColor: theme.colors.primary,
    padding: theme.spacing.md,
    borderRadius: theme.spacing.sm,
    minWidth: 100,
    alignItems: 'center',
  },
  statCategory: {
    color: theme.colors.white,
    fontSize: theme.fontSize.sm,
    marginBottom: theme.spacing.xs,
  },
  statCount: {
    color: theme.colors.white,
    fontSize: theme.fontSize.lg,
    fontWeight: 'bold',
  },
  patternList: {
    padding: theme.spacing.md,
    gap: theme.spacing.md,
  },
  patternItem: {
    backgroundColor: theme.colors.surface,
    padding: theme.spacing.md,
    borderRadius: theme.spacing.sm,
    shadowColor: theme.colors.grey5,
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  category: {
    fontSize: theme.fontSize.lg,
    fontWeight: 'bold',
    color: theme.colors.primary,
    marginBottom: theme.spacing.xs,
  },
  text: {
    fontSize: theme.fontSize.md,
    color: theme.colors.text,
    marginBottom: theme.spacing.xs,
  },
  confidence: {
    fontSize: theme.fontSize.sm,
    color: theme.colors.grey3,
    marginBottom: theme.spacing.sm,
  },
  rulesContainer: {
    marginTop: theme.spacing.sm,
  },
  rulesTitle: {
    fontSize: theme.fontSize.md,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: theme.spacing.xs,
  },
  rule: {
    fontSize: theme.fontSize.sm,
    color: theme.colors.text,
    marginLeft: theme.spacing.sm,
  },
}));
