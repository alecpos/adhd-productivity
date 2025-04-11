import React, { useState, useCallback } from 'react';
import { View } from 'react-native';

import { useRouter } from 'expo-router';
import { Text, makeStyles, useTheme, Tab, TabView } from '@rneui/themed';

import { useAuth } from '../../contexts/AuthContext';
import { useAutoClassifier } from '../../hooks/useAutoClassifier';
import * as Notifications from '../../contexts/ExpoNotificationsMock';
import { useToast } from '../components/ui/ToastProvider';

import ADHDDashboard from '../components/dashboard/ADHDDashboard';
import CalendarTab from '../components/dashboard/CalendarTab';
import FidgetTab from '../components/dashboard/FidgetTab';
import InsightsTab from '../components/dashboard/InsightsTab';
import TasksTab from '../components/dashboard/TasksTab';
import WellnessTab from '../components/dashboard/WellnessTab';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';

// Configure notifications
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
});

const useStyles = makeStyles((theme) => ({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  header: {
    padding: 16,
    backgroundColor: theme.colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  welcomeText: {
    color: theme.colors.text,
    fontSize: 20,
  },
  tabIndicator: {
    backgroundColor: theme.colors.primary,
    height: 3,
  },
  tabTitle: {
    fontSize: 14,
    color: theme.colors.text,
  },
  tabContent: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
}));

export default function DashboardScreen(): JSX.Element | null {
  const { user } = useAuth();
  const { theme: appTheme } = useTheme();
  const styles = useStyles();
  const router = useRouter();
  const { showToast } = useToast();
  const [tabIndex, setTabIndex] = useState(0);
  const { classifySubmission, getRecommendedActions } = useAutoClassifier();

  const handleSubmission = useCallback((text: string): void => {
    const classification = classifySubmission(text);
    const recommendedActions = getRecommendedActions(classification.category);

    if (classification.confidence > 0.7) {
      // Switch to appropriate tab based on classification
      switch (classification.category) {
        case 'task':
          setTabIndex(0);
          break;
        case 'wellness':
          setTabIndex(1);
          break;
        case 'calendar':
          setTabIndex(2);
          break;
        case 'insights':
          setTabIndex(3);
          break;
        case 'fidget':
          setTabIndex(4);
          break;
      }
    }
  }, [classifySubmission, getRecommendedActions]);

  if (!user) {
    return <LoadingSpinner />;
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text h4 style={styles.welcomeText}>
          Welcome back, {user.username}
        </Text>
      </View>

      <Tab
        value={tabIndex}
        onChange={setTabIndex}
        indicatorStyle={styles.tabIndicator}
        variant="primary"
      >
        <Tab.Item
          title="Tasks"
          titleStyle={styles.tabTitle}
          icon={{ name: 'tasks', type: 'font-awesome-5' }}
        />
        <Tab.Item
          title="Wellness"
          titleStyle={styles.tabTitle}
          icon={{ name: 'heart', type: 'font-awesome-5' }}
        />
        <Tab.Item
          title="Calendar"
          titleStyle={styles.tabTitle}
          icon={{ name: 'calendar', type: 'font-awesome-5' }}
        />
        <Tab.Item
          title="Insights"
          titleStyle={styles.tabTitle}
          icon={{ name: 'chart-line', type: 'font-awesome-5' }}
        />
        <Tab.Item
          title="Fidget"
          titleStyle={styles.tabTitle}
          icon={{ name: 'gamepad', type: 'font-awesome-5' }}
        />
      </Tab>

      <TabView
        value={tabIndex}
        onChange={setTabIndex}
        animationType="spring"
      >
        <TabView.Item style={styles.tabContent}>
          <TasksTab onSubmit={handleSubmission} />
        </TabView.Item>

        <TabView.Item style={styles.tabContent}>
          <WellnessTab />
        </TabView.Item>

        <TabView.Item style={styles.tabContent}>
          <CalendarTab />
        </TabView.Item>

        <TabView.Item style={styles.tabContent}>
          <ADHDDashboard />
        </TabView.Item>

        <TabView.Item style={styles.tabContent}>
          <FidgetTab />
        </TabView.Item>
      </TabView>
    </View>
  );
}
