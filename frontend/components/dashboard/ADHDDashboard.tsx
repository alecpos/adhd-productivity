import React, { useState, useCallback, useEffect } from 'react';

import { Text, Card, Button, Icon, Slider, useTheme } from '@rneui/themed';
import { View, ScrollView, StyleSheet } from 'react-native';

import { AnimatedButton } from '@/components/ui/AnimatedButton';
import { ErrorMessage } from '@/components/ui/ErrorMessage';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { useToast } from '@/components/ui/ToastProvider';
import { useADHDSettings } from '@/contexts/ADHDSettingsContext';
import { useMentalHealth } from '@/contexts/MentalHealthContext';
import { useADHDFocusTracking } from '@/hooks/useADHDFocusTracking';
import { useADHDTaskManagement } from '@/hooks/useADHDTaskManagement';
import { api } from '@/lib/api';

interface MentalHealthContextType {
  stats: MentalHealthStats | null;
  loading: boolean;
  error: string | null;
  logEnergyLevel: (level: number, activity: string) => Promise<void>;
  getStats: (startDate: Date, endDate: Date) => Promise<void>;
}

interface MentalHealthStats {
  mood_average: number;
  stress_level_average: number;
  anxiety_level_average: number;
  energy_level_average: number;
  focus_level_average: number;
  sleep_hours_average: number;
  sleep_quality_average: number;
  total_logs: number;
  recent_moods: Array<{
    date: string;
    mood: number;
    notes?: string;
  }>;
  streak: number;
  most_common_activities: string[];
  most_common_triggers: string[];
  most_common_coping_strategies: string[];
  updated_at: string;
}

const DEFAULT_RECOMMENDATIONS = [
  'Break tasks into smaller chunks',
  'Take regular breaks every 45 minutes',
  'Use visual aids and checklists',
  'Set reminders for transitions',
];

const DEFAULT_DAILY_PLAN = {
  focusBlocks: [
    { start: '09:00', end: '10:30', type: 'Deep Focus' },
    { start: '11:00', end: '12:00', type: 'Light Tasks' },
    { start: '14:00', end: '15:30', type: 'Creative Work' },
  ],
};

export default function ADHDDashboard() {
  const { theme } = useTheme();
  const { showToast } = useToast();
  const {
    profile,
    metrics,
    loading: settingsLoading,
    error: settingsError,
    logDistraction,
    logFocusSession,
    getRecommendations: getADHDRecommendations,
    generateDailyPlan,
  } = useADHDSettings();

  const {
    stats: mentalHealthStats,
    loading: mentalHealthLoading,
    error: mentalHealthError,
    getStats: getMentalHealthStats,
    createLog
  } = useMentalHealth();

  const [activeSection, setActiveSection] = useState<'focus' | 'energy' | 'plan'>('focus');
  const [currentEnergy, setCurrentEnergy] = useState(5);
  const [recommendations, setRecommendations] = useState<string[]>(DEFAULT_RECOMMENDATIONS);
  const [dailyPlan, setDailyPlan] = useState(DEFAULT_DAILY_PLAN);
  const [localError, setLocalError] = useState<string | null>(null);

  // Fetch initial data
  useEffect(() => {
    const loadData = async () => {
      try {
        // Get ADHD recommendations
        const recs = await getADHDRecommendations();
        if (recs?.strategies?.length > 0) {
          setRecommendations(recs.strategies);
        }

        // Get daily plan
        const plan = await generateDailyPlan(new Date());
        if (plan?.focusBlocks?.length > 0) {
          setDailyPlan(plan);
        }

        // Get mental health stats
        await getMentalHealthStats();

      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to load ADHD settings';
        setLocalError(errorMessage);
        showToast({
          type: 'error',
          message: 'Using offline recommendations. Some features may be limited.',
        });
      }
    };
    loadData();
  }, []);

  const handleLogDistraction = useCallback(async () => {
    try {
      await logDistraction('focus_break', 5, 3, 'Quick break needed');
      showToast({
        type: 'success',
        message: 'Break logged successfully',
      });
    } catch (err) {
      showToast({
        type: 'error',
        message: 'Failed to log break, but take one anyway!',
      });
    }
  }, [logDistraction, showToast]);

  const handleEnergyUpdate = useCallback(async (level: number) => {
    setCurrentEnergy(level);
    try {
      await createLog({
        moodScore: level,
        notes: 'Energy level update',
        stressLevel: 0
      });
      showToast({
        type: 'success',
        message: 'Energy level updated',
      });
    } catch (err) {
      showToast({
        type: 'error',
        message: 'Failed to update energy level',
      });
    }
  }, [createLog, showToast, setCurrentEnergy]);

  if (settingsLoading || mentalHealthLoading) {
    return <LoadingSpinner />;
  }

  return (
    <ScrollView style={styles.container}>
      {/* Quick Actions */}
      <Card containerStyle={styles.card}>
        <Card.Title>Quick Actions</Card.Title>
        <View style={styles.quickActions}>
          <AnimatedButton
            title="Need a Break"
            iconPosition="left"
            iconRight={false}
            icon={{
              name: 'coffee',
              type: 'font-awesome-5',
              color: theme.colors.white,
              size: 20,
            }}
            onPress={handleLogDistraction}
            scaleOnPress
            containerStyle={styles.actionButton}
            buttonStyle={{
              backgroundColor: theme.colors.primary,
              borderRadius: 8,
            }}
          />
          <AnimatedButton
            title="Start Focus Session"
            iconPosition="left"
            iconRight={false}
            icon={{
              name: 'brain',
              type: 'font-awesome-5',
              color: theme.colors.white,
              size: 20,
            }}
            onPress={() => setActiveSection('focus')}
            scaleOnPress
            containerStyle={styles.actionButton}
            buttonStyle={{
              backgroundColor: theme.colors.primary,
              borderRadius: 8,
            }}
          />
          <AnimatedButton
            title="View Daily Plan"
            iconPosition="left"
            iconRight={false}
            icon={{
              name: 'calendar-check',
              type: 'font-awesome-5',
              color: theme.colors.white,
              size: 20,
            }}
            onPress={() => setActiveSection('plan')}
            scaleOnPress
            containerStyle={styles.actionButton}
            buttonStyle={{
              backgroundColor: theme.colors.primary,
              borderRadius: 8,
            }}
          />
        </View>
      </Card>

      {/* Energy Level Tracker */}
      <Card containerStyle={styles.card}>
        <Card.Title>Current Energy Level</Card.Title>
        <View style={styles.energyTracker}>
          <Text style={styles.label}>How's your energy? (1-10)</Text>
          <Slider
            value={currentEnergy}
            onValueChange={handleEnergyUpdate}
            minimumValue={1}
            maximumValue={10}
            step={1}
            thumbStyle={{ backgroundColor: theme.colors.primary }}
            trackStyle={{ height: 4 }}
          />
          <Text style={styles.value}>{currentEnergy}</Text>
        </View>
      </Card>

      {/* Focus Stats */}
      {metrics && (
        <Card containerStyle={styles.card}>
          <Card.Title>Focus Insights</Card.Title>
          <View style={styles.statsContainer}>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>Daily Focus Score</Text>
              <Text style={styles.statValue}>{metrics.focusScores.daily.toFixed(1)}</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>Tasks Completed</Text>
              <Text style={styles.statValue}>
                {(metrics.taskCompletion.onTime * 100).toFixed(0)}%
              </Text>
            </View>
          </View>
        </Card>
      )}

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <Card containerStyle={styles.card}>
          <Card.Title>Today's Strategies</Card.Title>
          <View style={styles.recommendationsList}>
            {recommendations.map((rec, index) => (
              <View key={index} style={styles.recommendationItem}>
                <Icon
                  name="lightbulb"
                  type="font-awesome-5"
                  size={16}
                  color={theme.colors.primary}
                  style={styles.recommendationIcon}
                />
                <Text style={styles.recommendationText}>{rec}</Text>
              </View>
            ))}
          </View>
        </Card>
      )}

      {/* Daily Plan */}
      {dailyPlan && activeSection === 'plan' && (
        <Card containerStyle={styles.card}>
          <Card.Title>Your ADHD-Optimized Schedule</Card.Title>
          <View style={styles.planContainer}>
            {dailyPlan.focusBlocks.map((block: any, index: number) => (
              <View key={index} style={styles.timeBlock}>
                <Text style={styles.timeRange}>
                  {block.start} - {block.end}
                </Text>
                <Text style={styles.blockType}>{block.type}</Text>
              </View>
            ))}
          </View>
        </Card>
      )}

      {/* Mental Health Stats */}
      {mentalHealthStats && (
        <Card containerStyle={styles.card}>
          <Card.Title>Mental Health Overview</Card.Title>
          <View style={styles.statsContainer}>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>Mood Average</Text>
              <Text style={styles.statValue}>
                {mentalHealthStats.mood_average.toFixed(1)}/10
              </Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>Current Streak</Text>
              <Text style={styles.statValue}>
                {mentalHealthStats.streak} days
              </Text>
            </View>
          </View>
          {mentalHealthStats.recent_moods?.length > 0 && (
            <View style={styles.moodTrends}>
              <Text style={styles.sectionTitle}>Recent Moods</Text>
              {mentalHealthStats.recent_moods.map((mood, index: number) => (
                <View key={index} style={styles.moodItem}>
                  <Text style={styles.moodDate}>
                    {new Date(mood.date).toLocaleDateString()}
                  </Text>
                  <Text style={styles.moodScore}>{mood.mood}/10</Text>
                  {mood.notes && (
                    <Text style={styles.moodNotes}>{mood.notes}</Text>
                  )}
                </View>
              ))}
            </View>
          )}
        </Card>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  card: {
    borderRadius: 10,
    marginBottom: 15,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
  quickActions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    flexWrap: 'wrap',
    gap: 10,
  },
  actionButton: {
    minWidth: '30%',
    borderRadius: 8,
  },
  energyTracker: {
    marginVertical: 10,
  },
  label: {
    marginBottom: 5,
    fontSize: 16,
    fontWeight: '500',
  },
  value: {
    textAlign: 'center',
    marginTop: 5,
    fontSize: 16,
    fontWeight: 'bold',
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginVertical: 10,
  },
  statItem: {
    alignItems: 'center',
  },
  statLabel: {
    fontSize: 14,
    color: '#666',
    marginBottom: 5,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  recommendationsList: {
    gap: 10,
  },
  recommendationItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  recommendationIcon: {
    width: 24,
  },
  recommendationText: {
    flex: 1,
    fontSize: 14,
  },
  planContainer: {
    gap: 10,
  },
  timeBlock: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 10,
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
  },
  timeRange: {
    fontSize: 14,
    fontWeight: '500',
  },
  blockType: {
    fontSize: 14,
    color: '#666',
  },
  moodTrends: {
    marginTop: 10,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  moodItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 10,
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
  },
  moodDate: {
    fontSize: 14,
    color: '#666',
  },
  moodScore: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  moodNotes: {
    fontSize: 14,
    color: '#666',
  },
});
