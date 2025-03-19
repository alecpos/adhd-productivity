import React, { useState } from 'react';

import { Text, Card, Slider, useTheme, makeStyles } from '@rneui/themed';
import { View } from 'react-native';
import { Dimensions } from 'react-native';
import { LineChart } from 'react-native-chart-kit';

import { AnimatedButton } from './ui/AnimatedButton';


interface EnergyLog {
  level: number;
  timestamp: Date;
}

interface EnergyLevelTrackerProps {
  onUpdate: (energy: number) => void;
}

export function EnergyLevelTracker({ onUpdate }: EnergyLevelTrackerProps) {
  const { theme } = useTheme();
  const styles = useStyles();
  const [currentEnergy, setCurrentEnergy] = useState(5);
  const [energyLogs, setEnergyLogs] = useState<EnergyLog[]>([]);

  const handleLogEnergy = () => {
    const newLog: EnergyLog = {
      level: currentEnergy,
      timestamp: new Date(),
    };
    setEnergyLogs([...energyLogs, newLog]);
    onUpdate(currentEnergy);
  };

  const chartData = {
    labels: energyLogs.map(log => 
      log.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    ),
    datasets: [{
      data: energyLogs.map(log => log.level),
    }],
  };

  return (
    <Card containerStyle={styles.container}>
      <Card.Title>Energy Level Tracker</Card.Title>
      
      <View style={styles.currentEnergy}>
        <Text style={styles.label}>Current Energy Level (1-10)</Text>
        <Slider
          value={currentEnergy}
          onValueChange={setCurrentEnergy}
          minimumValue={1}
          maximumValue={10}
          step={1}
          thumbStyle={{ backgroundColor: theme.colors.primary }}
          trackStyle={{ height: theme.spacing.sm }}
        />
        <Text style={styles.value}>{currentEnergy}</Text>
        
        <AnimatedButton
          title="Log Energy Level"
          onPress={handleLogEnergy}
          scaleOnPress
          containerStyle={styles.button}
        />
      </View>

      {energyLogs.length > 0 && (
        <View style={styles.chartContainer}>
          <Text style={styles.chartTitle}>Energy Level Throughout Day</Text>
          <LineChart
            data={chartData}
            width={Dimensions.get('window').width - 60}
            height={220}
            chartConfig={{
              backgroundColor: theme.colors.background,
              backgroundGradientFrom: theme.colors.background,
              backgroundGradientTo: theme.colors.background,
              decimalPlaces: 0,
              color: (opacity = 1) => theme.colors.primary,
              labelColor: (opacity = 1) => theme.colors.grey3,
              style: {
                borderRadius: 16,
              },
            }}
            bezier
            style={styles.chart}
          />
        </View>
      )}
    </Card>
  );
}

const useStyles = makeStyles((theme) => ({
  container: {
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    marginBottom: theme.spacing.md,
  },
  currentEnergy: {
    marginBottom: theme.spacing.lg,
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
    marginTop: theme.spacing.md,
    borderRadius: theme.borderRadius.md,
    overflow: 'hidden',
  },
  chartContainer: {
    marginTop: theme.spacing.lg,
  },
  chartTitle: {
    fontSize: theme.fontSize.md,
    fontWeight: '500',
    marginBottom: theme.spacing.sm,
    textAlign: 'center',
    color: theme.colors.text,
  },
  chart: {
    marginVertical: theme.spacing.sm,
    borderRadius: theme.borderRadius.lg,
  },
}));