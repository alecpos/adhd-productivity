// app/(auth)/tasks/_layout.tsx
import React from 'react';

import { Stack } from 'expo-router';

export default function TasksLayout() {
  return (
    <Stack>
      <Stack.Screen name="index" options={{ title: 'Tasks' }} />
      <Stack.Screen name="create" options={{ title: 'Create Task' }} />
      <Stack.Screen name="[id]" options={{ title: 'Edit Task' }} />
    </Stack>
  );
}
