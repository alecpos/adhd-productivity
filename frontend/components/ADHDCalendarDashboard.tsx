import React, { useState } from 'react';
import { Card, Icon } from '@rneui/themed';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Dimensions } from 'react-native';

interface FeatureCard {
  id: string;
  title: string;
  icon: string;
  iconType: string;
  description: string;
  color: string;
  route: string;
  epic: number;
}

const featureCards: FeatureCard[] = [
  {
    id: 'productivity-patterns',
    title: 'Productivity Patterns',
    icon: 'chart-line',
    iconType: 'material-community',
    description: 'View your productivity patterns and insights based on historical data.',
    color: '#4782DA',
    route: 'ProductivityPatternViewer',
    epic: 1
  },
  {
    id: 'circadian-rhythm',
    title: 'Energy Patterns',
    icon: 'timelapse',
    iconType: 'material',
    description: 'Understand your energy levels throughout the day for optimal task scheduling.',
    color: '#47A6DA',
    route: 'CircadianRhythmView',
    epic: 1
  },
  {
    id: 'duration-estimator',
    title: 'Duration Estimator',
    icon: 'clock-time-eight-outline',
    iconType: 'material-community',
    description: 'Get more accurate time estimates for your tasks based on complexity.',
    color: '#8047DA',
    route: 'DurationEstimator',
    epic: 2
  },
  {
    id: 'commitment-tracker',
    title: 'Commitment Tracker',
    icon: 'checkbox-marked-circle-outline',
    iconType: 'material-community',
    description: 'Never forget a commitment with AI-powered detection and reminders.',
    color: '#DA47A0',
    route: 'CommitmentTracker',
    epic: 3
  },
  {
    id: 'schedule-optimizer',
    title: 'Schedule Optimizer',
    icon: 'calendar-clock',
    iconType: 'material-community',
    description: 'Dynamically rebalance your schedule based on energy levels and priorities.',
    color: '#47DA9B',
    route: 'ScheduleOptimizer',
    epic: 4
  },
  {
    id: 'explainable-ai',
    title: 'AI Explanations',
    icon: 'lightbulb-outline',
    iconType: 'material',
    description: 'Understand how our AI makes decisions with transparent explanations.',
    color: '#DAA147',
    route: 'ExplainableAI',
    epic: 5
  },
  {
    id: 'adaptive-ui',
    title: 'UI Preferences',
    icon: 'palette',
    iconType: 'material',
    description: 'Customize the interface for your neurodiversity needs and get rewards.',
    color: '#DA4747',
    route: 'AdaptiveUI',
    epic: 6
  }
];

interface ADHDCalendarDashboardProps {
  navigation?: any;
}

export const ADHDCalendarDashboard = ({ navigation }: ADHDCalendarDashboardProps) => {
  const [activeFilter, setActiveFilter] = useState<number | null>(null);

  const screenWidth = Dimensions.get('window').width;
  const cardWidth = screenWidth < 500 ? screenWidth - 40 : (screenWidth - 60) / 2;

  const filteredCards = activeFilter
    ? featureCards.filter(card => card.epic === activeFilter)
    : featureCards;

  const handleCardPress = (route: string) => {
    if (navigation) {
      navigation.navigate(route);
    } else {
      console.log(`Navigate to: ${route}`);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>ADHD Calendar</Text>
        <Text style={styles.subtitle}>All your tools in one place</Text>
      </View>

      <View style={styles.filterContainer}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          <TouchableOpacity
            style={[styles.filterButton, activeFilter === null && styles.activeFilter]}
            onPress={() => setActiveFilter(null)}
          >
            <Text style={[styles.filterText, activeFilter === null && styles.activeFilterText]}>All</Text>
          </TouchableOpacity>

          {[1, 2, 3, 4, 5, 6].map(epicNumber => (
            <TouchableOpacity
              key={epicNumber}
              style={[styles.filterButton, activeFilter === epicNumber && styles.activeFilter]}
              onPress={() => setActiveFilter(epicNumber)}
            >
              <Text style={[styles.filterText, activeFilter === epicNumber && styles.activeFilterText]}>
                Epic {epicNumber}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      <ScrollView style={styles.cardContainer}>
        <View style={styles.cardGrid}>
          {filteredCards.map(card => (
            <TouchableOpacity
              key={card.id}
              style={[styles.cardWrapper, { width: cardWidth }]}
              onPress={() => handleCardPress(card.route)}
            >
              <Card containerStyle={[styles.card, { borderLeftColor: card.color }]}>
                <View style={styles.cardHeader}>
                  <View style={[styles.iconCircle, { backgroundColor: card.color }]}>
                    <Icon
                      name={card.icon}
                      type={card.iconType}
                      color="white"
                      size={24}
                    />
                  </View>

                  <View style={styles.epicBadge}>
                    <Text style={styles.epicText}>Epic {card.epic}</Text>
                  </View>
                </View>

                <Text style={styles.cardTitle}>{card.title}</Text>
                <Text style={styles.cardDescription}>{card.description}</Text>

                <View style={styles.cardFooter}>
                  <Text style={styles.openText}>Open</Text>
                  <Icon
                    name="chevron-right"
                    type="material"
                    color="#888"
                    size={18}
                  />
                </View>
              </Card>
            </TouchableOpacity>
          ))}
        </View>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    padding: 20,
    backgroundColor: '#4782DA',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
  },
  subtitle: {
    fontSize: 16,
    color: 'rgba(255, 255, 255, 0.8)',
    marginTop: 5,
  },
  filterContainer: {
    backgroundColor: 'white',
    paddingVertical: 10,
    paddingHorizontal: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  filterButton: {
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 10,
    backgroundColor: '#f0f0f0',
  },
  activeFilter: {
    backgroundColor: '#4782DA',
  },
  filterText: {
    fontSize: 14,
    color: '#666666',
  },
  activeFilterText: {
    color: 'white',
    fontWeight: 'bold',
  },
  cardContainer: {
    flex: 1,
    padding: 10,
  },
  cardGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  cardWrapper: {
    marginBottom: 15,
  },
  card: {
    borderRadius: 10,
    padding: 15,
    borderLeftWidth: 4,
    margin: 5,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 10,
  },
  iconCircle: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  epicBadge: {
    backgroundColor: '#f0f0f0',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 10,
  },
  epicText: {
    fontSize: 12,
    color: '#666666',
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  cardDescription: {
    fontSize: 14,
    color: '#666666',
    marginBottom: 15,
  },
  cardFooter: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    alignItems: 'center',
  },
  openText: {
    fontSize: 14,
    color: '#888888',
    marginRight: 5,
  },
});
