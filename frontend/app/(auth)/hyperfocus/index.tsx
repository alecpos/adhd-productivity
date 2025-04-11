// app/(auth)/hyperfocus/index.tsx
import React, { Suspense, useState, useEffect } from 'react';

import { Text, Card, Button, makeStyles } from '@rneui/themed';
import { View } from 'react-native';

import { useAuth } from 'contexts/AuthContext';
import { useHyperfocus } from 'contexts/HyperfocusContext';

import { LoadingSpinner } from '@/app/components/ui/LoadingSpinner';
import type { HyperfocusSessionStats } from '@/core/api/services/hyperfocusService';
import { taskService, TaskPriority, TaskStatus } from '@/core/api/services/taskService';
import { Task } from '@/core/types';

// Lazy load components using correct paths from the index
const Analytics = React.lazy(() => import('@/app/components/Analytics'));
const GamificationDashboard = React.lazy(() =>
  import('@/app/components/gamification/components/GamificationDashboard')
);

export default function HyperfocusScreen() {
  const { sessions, loading, startSession, endSession, getSessionStats } = useHyperfocus();
  const { user } = useAuth();
  const [stats, setStats] = useState<HyperfocusSessionStats | null>(null);
  const [activeSession, setActiveSession] = useState<string | null>(null);
  const styles = useStyles();

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const sessionStats = await getSessionStats();
        if (sessionStats) {
          setStats(sessionStats);
        }
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      }
    };
    fetchStats();
  }, [getSessionStats]);

  const handleStartSession = async () => {
    try {
      if (!user?.id) {
        console.error('User not authenticated');
        return;
      }

      // Create a task first
      const task = await taskService.createTask({
        user_id: user.id,
        title: 'Focus session task',
        description: 'Task created for focus session',
        priority: TaskPriority.MEDIUM,
        estimated_duration: 25,
        energy_required: 5
      });

      // Start hyperfocus session with the created task
      const session = await startSession({
        duration_minutes: 25,
        task_id: task.id,
        purpose: 'Focus session for: ' + task.title,
        focus_area: 'Task Focus',
        tools_used: ['timer', 'noise-cancellation']
      });
      setActiveSession(session.id);
    } catch (error) {
      console.error('Failed to start session:', error);
    }
  };

  const handleEndSession = async () => {
    if (!activeSession) return;
    try {
      await endSession(activeSession);
      setActiveSession(null);
    } catch (error) {
      console.error('Failed to end session:', error);
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <View style={styles.container}>
      <Card containerStyle={styles.card}>
        {activeSession ? (
          <>
            <Text h4>Session Active</Text>
            <Text style={styles.timerText}>Session in progress</Text>
            <Button
              title="End Session"
              onPress={handleEndSession}
              containerStyle={styles.buttonContainer}
              buttonStyle={styles.endButton}
            />
          </>
        ) : (
          <Button
            title="Start Session"
            onPress={handleStartSession}
            containerStyle={styles.buttonContainer}
            buttonStyle={styles.startButton}
          />
        )}
        <Text style={styles.streakText}>
          Total Sessions: {stats?.total_sessions || 0}
        </Text>
      </Card>

      <React.Suspense fallback={<LoadingSpinner />}>
        <Analytics />
        <GamificationDashboard
          streaks={{
            current_streak: stats?.total_sessions || 0,
            highest_streak: stats?.completion_rate || 0,
            badges: []
          }}
          leaderboard={[]}
        />
      </React.Suspense>
    </View>
  );
}

const useStyles = makeStyles((theme) => ({
  container: {
    flex: 1,
    padding: theme.spacing.md,
    backgroundColor: theme.colors.background,
  },
  card: {
    borderRadius: theme.borderRadius.md,
    marginBottom: theme.spacing.md,
  },
  timerText: {
    fontSize: theme.fontSize.xl, // Large size for timer
    fontWeight: 'bold',
    textAlign: 'center',
    color: theme.colors.primary,
  },
  inactiveText: {
    fontSize: theme.fontSize.md,
    textAlign: 'center',
    color: theme.colors.grey3,
  },
  buttonContainer: {
    marginTop: theme.spacing.md,
  },
  startButton: {
    backgroundColor: theme.colors.success,
    borderRadius: theme.borderRadius.sm,
  },
  endButton: {
    backgroundColor: theme.colors.error,
    borderRadius: theme.borderRadius.sm,
  },
  streakText: {
    marginTop: theme.spacing.lg,
    fontSize: theme.fontSize.md,
    fontStyle: "italic",
    textAlign: "center",
    color: theme.colors.grey2,
  }
}));
