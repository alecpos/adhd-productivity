import React from 'react';

import { makeStyles } from '@rneui/themed';
import { View, ScrollView } from 'react-native';

import Analytics from '../../components/Analytics';
import GamificationDashboard from '../gamification/components/GamificationDashboard';
import PatternVisualizer from '../PatternVisualizer';

export default function InsightsTab() {
  const styles = useStyles();

  return (
    <ScrollView style={styles.container}>
      <View style={styles.section}>
        <Analytics />
      </View>

      <View style={styles.section}>
        <PatternVisualizer />
      </View>

      <View style={styles.section}>
        <GamificationDashboard
          streaks={{
            current_streak: 0,
            highest_streak: 0,
            badges: []
          }}
          leaderboard={[]}
        />
      </View>
    </ScrollView>
  );
}

const useStyles = makeStyles((theme) => ({
  container: {
    flex: 1,
  },
  section: {
    marginVertical: theme.spacing.sm,
    padding: theme.spacing.md,
    backgroundColor: theme.colors.surface,
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
}));
