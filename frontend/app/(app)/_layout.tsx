import { useEffect } from 'react';

import { Ionicons } from '@expo/vector-icons';
import { Tabs } from 'expo-router';
import { useRouter } from 'expo-router';

import { useAuth } from '@/contexts/AuthContext';

interface TabBarIconProps {
  color: string;
  size: number;
}

export default function AppLayout() {
  const { user, isInitialized, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isInitialized && !loading && !user) {
      router.replace('/(unauth)/login');
    }
  }, [user, isInitialized, loading, router]);

  if (!isInitialized || loading || !user) return null;

  return (
    <Tabs
      screenOptions={{
        headerShown: false,
      }}
    >
      <Tabs.Screen
        name="tasks"
        options={{
          title: 'Tasks',
          tabBarLabel: 'Tasks',
          tabBarIcon: ({ color, size }: TabBarIconProps) => (
            <Ionicons name="list-outline" size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="wellness"
        options={{
          title: 'Wellness',
          tabBarLabel: 'Wellness',
          tabBarIcon: ({ color, size }: TabBarIconProps) => (
            <Ionicons name="heart-outline" size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="calendar"
        options={{
          title: 'Calendar',
          tabBarLabel: 'Calendar',
          tabBarIcon: ({ color, size }: TabBarIconProps) => (
            <Ionicons name="calendar-outline" size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="insights"
        options={{
          title: 'Insights',
          tabBarLabel: 'Insights',
          tabBarIcon: ({ color, size }: TabBarIconProps) => (
            <Ionicons name="analytics-outline" size={size} color={color} />
          ),
        }}
      />
    </Tabs>
  );
} 