import React from 'react';

import { Text, Card, useTheme, makeStyles } from '@rneui/themed';
import { View, Dimensions } from 'react-native';
import { LineChart } from 'react-native-chart-kit';

export function Analytics() {
  const { theme } = useTheme();
  const styles = useStyles();
  
  // Example data - replace with actual data from your backend
  const mentalHealthData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        data: [7, 6, 8, 5, 7, 8, 6], // Mood
        color: (opacity = 1) => theme.colors.primary,
        strokeWidth: 2,
      },
      {
        data: [4, 5, 3, 6, 4, 3, 5], // Anxiety
        color: (opacity = 1) => theme.colors.error,
        strokeWidth: 2,
      },
    ],
    legend: ['Mood', 'Anxiety'],
  };

  const focusData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [{
      data: [3, 4, 2, 5, 3, 4, 3], // Hours focused
      color: (opacity = 1) => theme.colors.primary,
      strokeWidth: 2,
    }],
  };

  const chartConfig = {
    backgroundColor: theme.colors.background,
    backgroundGradientFrom: theme.colors.background,
    backgroundGradientTo: theme.colors.background,
    decimalPlaces: 1,
    color: (opacity = 1) => theme.colors.primary,
    labelColor: (opacity = 1) => theme.colors.grey3,
    style: {
      borderRadius: 16,
    },
    propsForDots: {
      r: '6',
      strokeWidth: '2',
      stroke: theme.colors.primary,
    },
  };

  return (
    <Card containerStyle={styles.container}>
      <Card.Title>Weekly Analytics</Card.Title>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Mental Health Trends</Text>
        <LineChart
          data={mentalHealthData}
          width={Dimensions.get('window').width - 60}
          height={220}
          chartConfig={chartConfig}
          bezier
          style={styles.chart}
          withInnerLines={false}
          withOuterLines={false}
          withDots
          withShadow={false}
        />
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Focus Time</Text>
        <LineChart
          data={focusData}
          width={Dimensions.get('window').width - 60}
          height={220}
          chartConfig={chartConfig}
          style={styles.chart}
          withInnerLines={false}
          withOuterLines={false}
          withDots
          withShadow={false}
        />
      </View>

      <View style={styles.statsContainer}>
        <View style={styles.statItem}>
          <Text style={styles.statValue}>85%</Text>
          <Text style={styles.statLabel}>Task Completion</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statValue}>4.2h</Text>
          <Text style={styles.statLabel}>Avg. Focus Time</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statValue}>7.2</Text>
          <Text style={styles.statLabel}>Avg. Mood</Text>
        </View>
      </View>
    </Card>
  );
}

const useStyles = makeStyles((theme) => ({
  container: {
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    marginBottom: theme.spacing.md,
  },
  section: {
    marginBottom: theme.spacing.lg,
  },
  sectionTitle: {
    fontSize: theme.fontSize.md,
    fontWeight: '500',
    marginBottom: theme.spacing.md,
    marginLeft: theme.spacing.sm,
    color: theme.colors.text,
  },
  chart: {
    marginVertical: theme.spacing.sm,
    borderRadius: theme.borderRadius.lg,
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginTop: theme.spacing.sm,
  },
  statItem: {
    alignItems: 'center',
  },
  statValue: {
    fontSize: theme.fontSize.xl,
    fontWeight: 'bold',
    color: theme.colors.primary,
  },
  statLabel: {
    fontSize: theme.fontSize.xs,
    color: theme.colors.grey3,
    marginTop: theme.spacing.xs,
  },
}));