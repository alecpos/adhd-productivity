import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { Card, Button, Icon, Divider, Slider, Badge } from '@rneui/themed';
import { Dimensions } from 'react-native';
import { LineChart } from 'react-native-chart-kit';

interface ScheduleBlock {
  id: string;
  title: string;
  startTime: string;
  endTime: string;
  category: 'work' | 'personal' | 'health' | 'learning';
  energyLevel: 'high' | 'medium' | 'low';
  priority: 'high' | 'medium' | 'low';
  isOptimal: boolean;
  isBreak?: boolean;
}

interface OptimizerSettings {
  energyAware: boolean;
  includeFocusBlocks: boolean;
  includeBreaks: boolean;
  breakFrequency: number; // minutes between breaks
  respectPriorities: boolean;
  rebalanceThreshold: number; // 0-1
}

// Mock schedule data
const originalSchedule: ScheduleBlock[] = [
  {
    id: '1',
    title: 'Project planning meeting',
    startTime: '09:00',
    endTime: '10:00',
    category: 'work',
    energyLevel: 'high',
    priority: 'high',
    isOptimal: true
  },
  {
    id: '2',
    title: 'Email responses',
    startTime: '10:00',
    endTime: '10:45',
    category: 'work',
    energyLevel: 'medium',
    priority: 'medium',
    isOptimal: false
  },
  {
    id: '3',
    title: 'Code review',
    startTime: '10:45',
    endTime: '12:00',
    category: 'work',
    energyLevel: 'high',
    priority: 'high',
    isOptimal: false
  },
  {
    id: '4',
    title: 'Lunch',
    startTime: '12:00',
    endTime: '13:00',
    category: 'personal',
    energyLevel: 'low',
    priority: 'medium',
    isOptimal: true
  },
  {
    id: '5',
    title: 'Documentation writing',
    startTime: '13:00',
    endTime: '15:00',
    category: 'work',
    energyLevel: 'medium',
    priority: 'medium',
    isOptimal: false
  },
  {
    id: '6',
    title: 'Team brainstorming',
    startTime: '15:00',
    endTime: '16:30',
    category: 'work',
    energyLevel: 'medium',
    priority: 'high',
    isOptimal: true
  },
  {
    id: '7',
    title: 'Project progress update',
    startTime: '16:30',
    endTime: '17:00',
    category: 'work',
    energyLevel: 'low',
    priority: 'high',
    isOptimal: false
  }
];

// Mock optimized schedule with changes
const optimizedSchedule: ScheduleBlock[] = [
  {
    id: '1',
    title: 'Project planning meeting',
    startTime: '09:00',
    endTime: '10:00',
    category: 'work',
    energyLevel: 'high',
    priority: 'high',
    isOptimal: true
  },
  {
    id: '3', // Moved code review earlier when energy is higher
    title: 'Code review',
    startTime: '10:00',
    endTime: '11:15',
    category: 'work',
    energyLevel: 'high',
    priority: 'high',
    isOptimal: true
  },
  {
    id: 'break1',
    title: 'Short break',
    startTime: '11:15',
    endTime: '11:30',
    category: 'health',
    energyLevel: 'low',
    priority: 'low',
    isOptimal: true,
    isBreak: true
  },
  {
    id: '2', // Email moved to later
    title: 'Email responses',
    startTime: '11:30',
    endTime: '12:00',
    category: 'work',
    energyLevel: 'medium',
    priority: 'medium',
    isOptimal: true
  },
  {
    id: '4',
    title: 'Lunch',
    startTime: '12:00',
    endTime: '13:00',
    category: 'personal',
    energyLevel: 'low',
    priority: 'medium',
    isOptimal: true
  },
  {
    id: '6', // Team brainstorming moved earlier
    title: 'Team brainstorming',
    startTime: '13:00',
    endTime: '14:30',
    category: 'work',
    energyLevel: 'medium',
    priority: 'high',
    isOptimal: true
  },
  {
    id: 'break2',
    title: 'Short break',
    startTime: '14:30',
    endTime: '14:45',
    category: 'health',
    energyLevel: 'low',
    priority: 'low',
    isOptimal: true,
    isBreak: true
  },
  {
    id: '5',
    title: 'Documentation writing',
    startTime: '14:45',
    endTime: '16:15',
    category: 'work',
    energyLevel: 'medium',
    priority: 'medium',
    isOptimal: true
  },
  {
    id: '7',
    title: 'Project progress update',
    startTime: '16:15',
    endTime: '16:45',
    category: 'work',
    energyLevel: 'low',
    priority: 'high',
    isOptimal: true
  },
  {
    id: 'break3',
    title: 'Reflection time',
    startTime: '16:45',
    endTime: '17:00',
    category: 'personal',
    energyLevel: 'low',
    priority: 'medium',
    isOptimal: true,
    isBreak: true
  }
];

// Mock energy data for the day
const energyData = {
  labels: ['6AM', '9AM', '12PM', '3PM', '6PM', '9PM'],
  datasets: [
    {
      data: [30, 80, 65, 75, 55, 40],
      color: (opacity = 1) => `rgba(71, 136, 218, ${opacity})`,
      strokeWidth: 2
    }
  ]
};

export const ScheduleOptimizer = () => {
  const [schedule, setSchedule] = useState<ScheduleBlock[]>(originalSchedule);
  const [isOptimized, setIsOptimized] = useState(false);
  const [showEnergyChart, setShowEnergyChart] = useState(true);
  const [settings, setSettings] = useState<OptimizerSettings>({
    energyAware: true,
    includeFocusBlocks: true,
    includeBreaks: true,
    breakFrequency: 90,
    respectPriorities: true,
    rebalanceThreshold: 0.7
  });
  const [showSettings, setShowSettings] = useState(false);

  const screenWidth = Dimensions.get('window').width - 40;

  // Toggle between original and optimized schedule
  const toggleOptimization = () => {
    setIsOptimized(prev => !prev);
    setSchedule(isOptimized ? originalSchedule : optimizedSchedule);
  };

  // Get color for task category
  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'work': return '#4782DA';
      case 'personal': return '#DA9647';
      case 'health': return '#47DA96';
      case 'learning': return '#8047DA';
      default: return '#888888';
    }
  };

  // Get color for energy level
  const getEnergyColor = (level: string) => {
    switch (level) {
      case 'high': return '#47DA96';
      case 'medium': return '#DAA147';
      case 'low': return '#DA4747';
      default: return '#888888';
    }
  };

  // Get color for priority
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return '#DA4747';
      case 'medium': return '#DAA147';
      case 'low': return '#47DA96';
      default: return '#888888';
    }
  };

  // Update settings
  const updateSetting = (key: keyof OptimizerSettings, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  // Chart configuration
  const chartConfig = {
    backgroundGradientFrom: "#ffffff",
    backgroundGradientTo: "#ffffff",
    decimalPlaces: 0,
    color: (opacity = 1) => `rgba(71, 136, 218, ${opacity})`,
    labelColor: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
    style: {
      borderRadius: 16,
    },
    propsForDots: {
      r: "6",
      strokeWidth: "2",
      stroke: "#4782DA"
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Card containerStyle={styles.card}>
        <Card.Title>Schedule Optimizer</Card.Title>
        <Text style={styles.subtitle}>
          Dynamically rebalance your schedule based on energy levels, priorities, and optimal focus times.
        </Text>

        <Button
          title={isOptimized ? "View Original Schedule" : "Optimize Schedule"}
          onPress={toggleOptimization}
          buttonStyle={isOptimized ? styles.secondaryButton : styles.primaryButton}
          containerStyle={styles.optimizeButtonContainer}
          icon={{
            name: isOptimized ? 'restore' : 'auto-fix-high',
            type: isOptimized ? 'material' : 'material-community',
            color: 'white',
            size: 20
          }}
          iconPosition="right"
        />

        {isOptimized && (
          <View style={styles.optimizationStats}>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>+25%</Text>
              <Text style={styles.statLabel}>Productivity</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>3</Text>
              <Text style={styles.statLabel}>Breaks Added</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>85%</Text>
              <Text style={styles.statLabel}>Energy Alignment</Text>
            </View>
          </View>
        )}

        <Button
          title="Optimizer Settings"
          type="outline"
          onPress={() => setShowSettings(!showSettings)}
          buttonStyle={styles.settingsButton}
          containerStyle={styles.settingsButtonContainer}
          icon={{
            name: 'settings',
            type: 'material',
            color: '#4782DA',
            size: 20
          }}
          iconPosition="right"
        />

        {showSettings && (
          <View style={styles.settingsContainer}>
            <View style={styles.settingRow}>
              <Text style={styles.settingLabel}>Energy-aware scheduling</Text>
              <Button
                title={settings.energyAware ? "ON" : "OFF"}
                onPress={() => updateSetting('energyAware', !settings.energyAware)}
                buttonStyle={settings.energyAware ? styles.toggleOnButton : styles.toggleOffButton}
                containerStyle={styles.toggleButton}
                titleStyle={styles.toggleButtonText}
              />
            </View>

            <View style={styles.settingRow}>
              <Text style={styles.settingLabel}>Include focus blocks</Text>
              <Button
                title={settings.includeFocusBlocks ? "ON" : "OFF"}
                onPress={() => updateSetting('includeFocusBlocks', !settings.includeFocusBlocks)}
                buttonStyle={settings.includeFocusBlocks ? styles.toggleOnButton : styles.toggleOffButton}
                containerStyle={styles.toggleButton}
                titleStyle={styles.toggleButtonText}
              />
            </View>

            <View style={styles.settingRow}>
              <Text style={styles.settingLabel}>Add smart breaks</Text>
              <Button
                title={settings.includeBreaks ? "ON" : "OFF"}
                onPress={() => updateSetting('includeBreaks', !settings.includeBreaks)}
                buttonStyle={settings.includeBreaks ? styles.toggleOnButton : styles.toggleOffButton}
                containerStyle={styles.toggleButton}
                titleStyle={styles.toggleButtonText}
              />
            </View>

            <View style={styles.settingRow}>
              <Text style={styles.settingLabel}>Break frequency: {settings.breakFrequency} minutes</Text>
            </View>
            <Slider
              value={settings.breakFrequency}
              onValueChange={(value) => updateSetting('breakFrequency', value)}
              minimumValue={30}
              maximumValue={120}
              step={15}
              thumbStyle={styles.sliderThumb}
              thumbTintColor="#4782DA"
              minimumTrackTintColor="#4782DA"
              maximumTrackTintColor="#e0e0e0"
              style={styles.slider}
            />

            <View style={styles.settingRow}>
              <Text style={styles.settingLabel}>Respect task priorities</Text>
              <Button
                title={settings.respectPriorities ? "ON" : "OFF"}
                onPress={() => updateSetting('respectPriorities', !settings.respectPriorities)}
                buttonStyle={settings.respectPriorities ? styles.toggleOnButton : styles.toggleOffButton}
                containerStyle={styles.toggleButton}
                titleStyle={styles.toggleButtonText}
              />
            </View>

            <View style={styles.settingRow}>
              <Text style={styles.settingLabel}>Rebalance threshold: {settings.rebalanceThreshold.toFixed(1)}</Text>
            </View>
            <Slider
              value={settings.rebalanceThreshold}
              onValueChange={(value) => updateSetting('rebalanceThreshold', value)}
              minimumValue={0.1}
              maximumValue={1.0}
              step={0.1}
              thumbStyle={styles.sliderThumb}
              thumbTintColor="#4782DA"
              minimumTrackTintColor="#4782DA"
              maximumTrackTintColor="#e0e0e0"
              style={styles.slider}
            />
          </View>
        )}
      </Card>

      <Card containerStyle={styles.card}>
        <View style={styles.energyChartHeader}>
          <Text style={styles.energyChartTitle}>Your Energy Pattern</Text>
          <Button
            type="clear"
            icon={{
              name: showEnergyChart ? 'chevron-up' : 'chevron-down',
              type: 'material-community',
              color: '#4782DA',
              size: 20
            }}
            onPress={() => setShowEnergyChart(!showEnergyChart)}
            buttonStyle={styles.chartToggleButton}
          />
        </View>

        {showEnergyChart && (
          <LineChart
            data={energyData}
            width={screenWidth}
            height={180}
            chartConfig={chartConfig}
            bezier
            style={styles.chart}
          />
        )}
      </Card>

      <Card containerStyle={styles.card}>
        <Card.Title>{isOptimized ? "Optimized Schedule" : "Current Schedule"}</Card.Title>

        {schedule.map((block, index) => (
          <View key={block.id} style={styles.scheduleBlock}>
            <View style={styles.timeContainer}>
              <Text style={styles.timeText}>{block.startTime}</Text>
              <View style={styles.timeLine} />
              <Text style={styles.timeText}>{block.endTime}</Text>
            </View>

            <View style={[
              styles.blockContent,
              block.isBreak && styles.breakBlock
            ]}>
              <View style={styles.blockHeader}>
                <View style={styles.titleContainer}>
                  <Text style={styles.blockTitle}>{block.title}</Text>
                  <View style={styles.tagsContainer}>
                    <Badge
                      value={block.category}
                      containerStyle={styles.badgeContainer}
                      badgeStyle={{ backgroundColor: getCategoryColor(block.category) }}
                    />
                    <Badge
                      value={`Energy: ${block.energyLevel}`}
                      containerStyle={styles.badgeContainer}
                      badgeStyle={{ backgroundColor: getEnergyColor(block.energyLevel) }}
                    />
                    <Badge
                      value={`Priority: ${block.priority}`}
                      containerStyle={styles.badgeContainer}
                      badgeStyle={{ backgroundColor: getPriorityColor(block.priority) }}
                    />
                  </View>
                </View>

                {isOptimized && block.isOptimal && (
                  <Icon
                    name="check-circle"
                    type="material"
                    color="#47DA96"
                    size={24}
                  />
                )}
              </View>

              {isOptimized && index > 0 && block.id !== originalSchedule[index - 1]?.id && !block.isBreak && (
                <View style={styles.changeIndicator}>
                  <Icon name="arrow-upward" type="material" color="#4782DA" size={16} />
                  <Text style={styles.changeText}>Moved from later in day</Text>
                </View>
              )}

              {isOptimized && block.isBreak && (
                <View style={styles.changeIndicator}>
                  <Icon name="plus-circle" type="material-community" color="#47DA96" size={16} />
                  <Text style={styles.changeText}>Added break to optimize focus</Text>
                </View>
              )}
            </View>
          </View>
        ))}
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
  subtitle: {
    fontSize: 14,
    textAlign: 'center',
    marginBottom: 15,
    color: '#666666',
  },
  optimizeButtonContainer: {
    marginBottom: 15,
  },
  primaryButton: {
    backgroundColor: '#4782DA',
    borderRadius: 8,
    padding: 12,
  },
  secondaryButton: {
    backgroundColor: '#47A6DA',
    borderRadius: 8,
    padding: 12,
  },
  optimizationStats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginVertical: 15,
    backgroundColor: '#f0f7ff',
    borderRadius: 8,
    padding: 10,
  },
  statItem: {
    alignItems: 'center',
  },
  statValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#4782DA',
  },
  statLabel: {
    fontSize: 12,
    color: '#666666',
  },
  settingsButtonContainer: {
    marginTop: 5,
  },
  settingsButton: {
    borderColor: '#4782DA',
    borderRadius: 8,
  },
  settingsContainer: {
    marginTop: 15,
    backgroundColor: '#f8f8f8',
    borderRadius: 8,
    padding: 12,
  },
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  settingLabel: {
    fontSize: 14,
    color: '#333333',
    flex: 1,
  },
  toggleButton: {
    width: 60,
  },
  toggleOnButton: {
    backgroundColor: '#4782DA',
    borderRadius: 12,
    padding: 5,
  },
  toggleOffButton: {
    backgroundColor: '#cccccc',
    borderRadius: 12,
    padding: 5,
  },
  toggleButtonText: {
    fontSize: 12,
  },
  slider: {
    marginBottom: 15,
  },
  sliderThumb: {
    width: 20,
    height: 20,
    borderRadius: 10,
  },
  energyChartHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  energyChartTitle: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  chartToggleButton: {
    padding: 0,
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
  scheduleBlock: {
    flexDirection: 'row',
    marginBottom: 15,
  },
  timeContainer: {
    width: 70,
    alignItems: 'center',
  },
  timeText: {
    fontSize: 14,
    color: '#666666',
  },
  timeLine: {
    flex: 1,
    width: 2,
    backgroundColor: '#e0e0e0',
    marginVertical: 4,
  },
  blockContent: {
    flex: 1,
    borderLeftWidth: 3,
    borderLeftColor: '#4782DA',
    backgroundColor: '#f9f9f9',
    borderRadius: 8,
    padding: 12,
  },
  breakBlock: {
    borderLeftColor: '#47DA96',
    backgroundColor: '#f0fff5',
  },
  blockHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  titleContainer: {
    flex: 1,
  },
  blockTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  tagsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  badgeContainer: {
    marginRight: 5,
    marginBottom: 5,
  },
  changeIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#e6f0ff',
    padding: 8,
    borderRadius: 6,
    marginTop: 8,
  },
  changeText: {
    fontSize: 12,
    color: '#4782DA',
    marginLeft: 5,
  },
});
