import { useEffect } from 'react';

import { Stack } from 'expo-router';
import { useRouter } from 'expo-router';

import { useAuth } from '@/contexts/AuthContext';

export default function UnauthLayout() {
  const { isAuthenticated, isInitialized } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isInitialized && isAuthenticated) {
      const timer = setTimeout(() => {
        router.replace('/(auth)');
      }, 0);
      return () => clearTimeout(timer);
    }
  }, [isInitialized, isAuthenticated, router]);

  if (!isInitialized) {
    return null;
  }

  return (
    <Stack
      screenOptions={{
        headerShown: false,
        animation: 'fade',
      }}
    >
      <Stack.Screen name="login" options={{ title: 'Login' }} />
      <Stack.Screen name="register" options={{ title: 'Register' }} />
    </Stack>
  );
}
