import React, { useState } from 'react';

import { Card, Button, Slider } from '@rneui/themed';
import { View, Text, StyleSheet, ScrollView, Dimensions } from 'react-native';

import { LineChart } from 'react-native-chart-kit';

import { useAccessibilityPreferences } from '../../hooks/useAccessibilityPreferences';
import { useTheme } from '../../theme';

type EnergyLevel = 'low' | 'medium' | 'high';

interface TaskType {
  id: string;
  name: string;
  energyRequired: EnergyLevel;
  bestEnergyLevel: EnergyLevel;
  color: string;
}

const taskTypes: TaskType[] = [
  { id: '1', name: 'Deep Work', energyRequired: 'high', bestEnergyLevel: 'high', color: '#4782DA' },
  { id: '2', name: 'Admin Tasks', energyRequired: 'medium', bestEnergyLevel: 'medium', color: '#47DA9B' },
  { id: '3', name: 'Creative Work', energyRequired: 'high', bestEnergyLevel: 'medium', color: '#DA47A0' },
  { id: '4', name: 'Routine Tasks', energyRequired: 'low', bestEnergyLevel: 'low', color: '#DAA147' },
  { id: '5', name: 'Learning', energyRequired: 'high', bestEnergyLevel: 'high', color: '#6247DA' },
];

interface CircadianData {
  datasets: {
    data: number[];
    color?: (opacity: number) => string;
    strokeWidth?: number;
  }[];
  labels: string[];
}

// Mock energy level data for a typical day
const defaultCircadianData: CircadianData = {
  labels: ['6AM', '9AM', '12PM', '3PM', '6PM', '9PM', '12AM'],
  datasets: [
    {
      data: [40, 72, 65, 58, 75, 60, 35],
      color: (opacity = 1) => `rgba(71, 130, 218, ${opacity})`,
      strokeWidth: 2
    }
  ]
};

export const CircadianRhythmView = () => {
  const [selectedDay, setSelectedDay] = useState<'today' | 'tomorrow' | 'typical'>('typical');
  const [selectedTaskType, setSelectedTaskType] = useState<string | null>(null);
  const [highFocusMinutes, setHighFocusMinutes] = useState(180); // 3 hours default
  const { theme } = useTheme();
  const { reduceMotion, highContrast } = useAccessibilityPreferences();

  const screenWidth = Dimensions.get('window').width - 40;

  const chartConfig = {
    backgroundGradientFrom: theme.colors.background,
    backgroundGradientTo: theme.colors.background,
    decimalPlaces: 0,
    color: (opacity = 1) => highContrast
      ? `rgba(255, 255, 255, ${opacity})`
      : `rgba(71, 130, 218, ${opacity})`,
    labelColor: (opacity = 1) => `rgba(${highContrast ? '255, 255, 255' : theme.dark ? '255, 255, 255' : '0, 0, 0'}, ${opacity})`,
    style: {
      borderRadius: 16,
    },
    propsForDots: {
      r: "6",
      strokeWidth: "2",
      stroke: theme.colors.primary
    }
  };

  // Get optimal time blocks based on the current circadian curve and selected task type
  const getOptimalTimeBlocks = (): string[] => {
    if (!selectedTaskType) return [];

    const taskType = taskTypes.find(t => t.id === selectedTaskType);
    if (!taskType) return [];

    // In a real app, this would come from the backend based on CircadianRhythmModel calculations
    switch (taskType.bestEnergyLevel) {
      case 'high':
        return ['9:00 AM - 11:00 AM', '5:00 PM - 6:30 PM'];
      case 'medium':
        return ['11:30 AM - 1:30 PM', '3:00 PM - 4:30 PM'];
      case 'low':
        return ['6:30 AM - 8:00 AM', '7:00 PM - 8:30 PM'];
      default:
        return [];
    }
  };

  const getEnergyLevelColor = (level: number) => {
    if (level >= 70) return '#47DA9B'; // High energy - green
    if (level >= 50) return '#DAA147'; // Medium energy - amber
    return '#DA4747'; // Low energy - red
  };

  const formatMinutes = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}m`;
  };

  const optimalTimeBlocks = getOptimalTimeBlocks();

  return (
    <ScrollView style={styles.container}>
      <Card containerStyle={styles.card}>
        <Card.Title>Your Circadian Energy Pattern</Card.Title>

        <View style={styles.daySelector}>
          <Button
            title="Today"
            type={selectedDay === 'today' ? "solid" : "outline"}
            size="sm"
            onPress={() => setSelectedDay('today')}
            buttonStyle={styles.selectorButton}
            containerStyle={styles.selectorButtonContainer}
          />
          <Button
            title="Tomorrow"
            type={selectedDay === 'tomorrow' ? "solid" : "outline"}
            size="sm"
            onPress={() => setSelectedDay('tomorrow')}
            buttonStyle={styles.selectorButton}
            containerStyle={styles.selectorButtonContainer}
          />
          <Button
            title="Typical"
            type={selectedDay === 'typical' ? "solid" : "outline"}
            size="sm"
            onPress={() => setSelectedDay('typical')}
            buttonStyle={styles.selectorButton}
            containerStyle={styles.selectorButtonContainer}
          />
        </View>

        <LineChart
          data={defaultCircadianData}
          width={screenWidth}
          height={220}
          chartConfig={chartConfig}
          bezier
          style={styles.chart}
          withDots={!reduceMotion}
          withInnerLines={!reduceMotion}
          withOuterLines={!reduceMotion}
          withShadow={!reduceMotion}
          withVerticalLabels={true}
          withHorizontalLabels={true}
        />

        <Text style={styles.explanation}>
          This chart shows your predicted energy levels throughout the day.
          Your peak energy times are typically around 9:00 AM and 5:00 PM.
        </Text>
      </Card>

      <Card containerStyle={styles.card}>
        <Card.Title>Optimize Your Schedule</Card.Title>

        <Text style={styles.sectionTitle}>Task Type</Text>
        <View style={styles.taskTypeContainer}>
          {taskTypes.map((task) => (
            <Button
              key={task.id}
              title={task.name}
              type={selectedTaskType === task.id ? "solid" : "outline"}
              size="sm"
              buttonStyle={[
                styles.taskButton,
                { backgroundColor: selectedTaskType === task.id ? task.color : 'transparent',
                  borderColor: task.color }
              ]}
              titleStyle={{
                color: selectedTaskType === task.id ? 'white' : task.color
              }}
              onPress={() => setSelectedTaskType(task.id)}
              containerStyle={styles.taskButtonContainer}
            />
          ))}
        </View>

        <Text style={styles.sectionTitle}>High Focus Time Needed</Text>
        <View style={styles.sliderContainer}>
          <Slider
            value={highFocusMinutes}
            onValueChange={setHighFocusMinutes}
            minimumValue={30}
            maximumValue={360}
            step={15}
            thumbStyle={styles.sliderThumb}
            thumbTintColor={theme.colors.primary}
            minimumTrackTintColor={theme.colors.primary}
            maximumTrackTintColor={theme.colors.grey5}
          />
          <Text style={styles.sliderValue}>{formatMinutes(highFocusMinutes)}</Text>
        </View>

        {selectedTaskType && (
          <Card containerStyle={styles.recommendationCard}>
            <Card.Title>Recommended Time Blocks</Card.Title>
            {optimalTimeBlocks.length > 0 ? (
              <>
                <Text style={styles.recommendationText}>
                  Based on your circadian rhythm and task requirements, here are your optimal time blocks:
                </Text>
                {optimalTimeBlocks.map((timeBlock, index) => (
                  <View key={index} style={styles.timeBlock}>
                    <View
                      style={[
                        styles.energyIndicator,
                        { backgroundColor: getEnergyLevelColor(index === 0 ? 75 : 68) }
                      ]}
                    />
                    <Text style={styles.timeBlockText}>{timeBlock}</Text>
                  </View>
                ))}
                <Text style={styles.recommendationFooter}>
                  These recommendations are based on your historical productivity data and
                  energy patterns, with an 82% prediction confidence.
                </Text>
              </>
            ) : (
              <Text style={styles.noDataText}>
                Select a task type to see recommended time blocks.
              </Text>
            )}
          </Card>
        )}
      </Card>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  card: {
    borderRadius: 10,
    marginBottom: 15,
    padding: 15,
  },
  daySelector: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginBottom: 15,
  },
  selectorButton: {
    borderRadius: 20,
  },
  selectorButtonContainer: {
    marginHorizontal: 5,
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
  explanation: {
    fontSize: 14,
    marginTop: 10,
    textAlign: 'center',
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginTop: 15,
    marginBottom: 10,
  },
  taskTypeContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
    marginBottom: 10,
  },
  taskButton: {
    borderRadius: 20,
    paddingHorizontal: 12,
  },
  taskButtonContainer: {
    margin: 5,
  },
  sliderContainer: {
    marginVertical: 15,
    paddingHorizontal: 10,
  },
  sliderThumb: {
    width: 20,
    height: 20,
    borderRadius: 10,
  },
  sliderValue: {
    textAlign: 'center',
    marginTop: 5,
    fontSize: 16,
    fontWeight: 'bold',
  },
  recommendationCard: {
    marginTop: 10,
    borderRadius: 8,
    backgroundColor: '#f8f9fa',
  },
  recommendationText: {
    fontSize: 14,
    marginBottom: 15,
  },
  timeBlock: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
    backgroundColor: '#ffffff',
    padding: 12,
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 1,
    elevation: 1,
  },
  energyIndicator: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 10,
  },
  timeBlockText: {
    fontSize: 16,
    fontWeight: '500',
  },
  recommendationFooter: {
    fontSize: 12,
    fontStyle: 'italic',
    marginTop: 15,
  },
  noDataText: {
    textAlign: 'center',
    marginVertical: 15,
  },
});
