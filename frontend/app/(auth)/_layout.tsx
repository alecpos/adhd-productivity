import { useEffect } from 'react';

import { Stack, useRouter } from 'expo-router';

import { useAuth } from '@/contexts/AuthContext';

export default function AuthLayout() {
  const router = useRouter();
  const { user, loading, isInitialized } = useAuth();

  useEffect(() => {
    if (isInitialized && !loading && !user) {
      router.replace('/(unauth)/login');
    }
  }, [user, loading, isInitialized, router]);

  if (!isInitialized || loading || !user) {
    return null;
  }

  return (
    <Stack
      screenOptions={{
        headerShown: false,
        animation: 'fade',
      }}
    >
      <Stack.Screen name="index" options={{ title: 'Home' }} />
      <Stack.Screen name="mental-health" options={{ title: 'Mental Health' }} />
      <Stack.Screen name="calendar-management" options={{ title: 'Calendar' }} />
      <Stack.Screen name="scheduling" options={{ title: 'Schedule' }} />
      <Stack.Screen name="calendar-settings" options={{ title: 'Settings' }} />
      <Stack.Screen name="fidget/index" options={{ title: 'Fidget Tools' }} />
    </Stack>
  );
}
