import React, { useState } from 'react';

import { Tabs } from 'expo-router';
import { View, StyleSheet } from 'react-native';

import AISchedulingAssistant from '../components/AISchedulingAssistant';
import SchedulingBlock from '../components/SchedulingBlock';

function ScheduleView() {
  const [scheduleBlocks] = useState([
    {
      startTime: new Date(2024, 2, 15, 9, 0),
      endTime: new Date(2024, 2, 15, 10, 30),
      type: 'focus' as const,
    },
    {
      startTime: new Date(2024, 2, 15, 10, 30),
      endTime: new Date(2024, 2, 15, 10, 45),
      type: 'break' as const,
    },
    {
      startTime: new Date(2024, 2, 15, 10, 45),
      endTime: new Date(2024, 2, 15, 12, 15),
      type: 'focus' as const,
    },
    {
      startTime: new Date(2024, 2, 15, 12, 15),
      endTime: new Date(2024, 2, 15, 12, 45),
      type: 'long-break' as const,
    },
  ]);

  return (
    <View style={styles.container}>
      <View style={styles.content}>
        {scheduleBlocks.map((block, index) => (
          <SchedulingBlock
            key={index}
            startTime={block.startTime}
            endTime={block.endTime}
            type={block.type}
          />
        ))}
      </View>
    </View>
  );
}

export default function SchedulingScreen() {
  return (
    <Tabs>
      <Tabs.Screen 
        name="schedule" 
        component={ScheduleView}
        options={{
          title: 'My Schedule'
        }}
      />
      <Tabs.Screen 
        name="ai-assistant" 
        component={AISchedulingAssistant}
        options={{
          title: 'AI Assistant'
        }}
      />
    </Tabs>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    padding: 16,
  },
}); 