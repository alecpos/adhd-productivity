import React, { useState } from 'react';

import { Text, Button, Input, Card } from '@rneui/themed';
import { View, StyleSheet, ScrollView } from 'react-native';

import { schedulingService } from '../services/schedulingService';

import type { SchedulingSuggestion, TimeBlock } from '../services/schedulingService';

export default function AISchedulingAssistant() {
  const [task, setTask] = useState('');
  const [hours, setHours] = useState('');
  const [loading, setLoading] = useState(false);
  const [suggestion, setSuggestion] = useState<SchedulingSuggestion | null>(null);

  const handleSchedulingRequest = async () => {
    if (!task || !hours) return;

    setLoading(true);
    try {
      const suggestion = await schedulingService.checkAvailability({
        taskName: task,
        requiredHours: parseFloat(hours),
      });
      setSuggestion(suggestion);
    } catch (error) {
      console.error('Error getting scheduling suggestion:', error);
      // Handle error appropriately
    } finally {
      setLoading(false);
    }
  };

  const handleAcceptSchedule = async (blocks: TimeBlock[]) => {
    try {
      await schedulingService.scheduleTask(blocks);
      // Clear form and show success message
      setTask('');
      setHours('');
      setSuggestion(null);
    } catch (error) {
      console.error('Error scheduling task:', error);
      // Handle error appropriately
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Card>
        <Card.Title>AI Scheduling Assistant</Card.Title>
        <Text style={styles.description}>
          Tell me what you need to work on and I'll find the best time in your schedule.
        </Text>
        
        <Input
          placeholder="What do you need to work on?"
          value={task}
          onChangeText={setTask}
        />
        
        <Input
          placeholder="How many hours do you need?"
          value={hours}
          onChangeText={setHours}
          keyboardType="numeric"
        />

        <Button
          title={loading ? "Checking Schedule..." : "Check Availability"}
          onPress={handleSchedulingRequest}
          loading={loading}
          disabled={loading || !task || !hours}
        />
      </Card>

      {suggestion && (
        <Card>
          <Card.Title>Scheduling Suggestions</Card.Title>
          
          <Text style={styles.confidence}>
            Confidence: {(suggestion.confidence * 100).toFixed(1)}%
          </Text>

          {suggestion.decisionTree.map((decision, index) => (
            <View key={index} style={styles.decision}>
              <Text style={styles.optionTitle}>Option {index + 1}</Text>
              <Text>{decision.reasoning}</Text>
              
              <View style={styles.timeBlocks}>
                {decision.timeBlocks.map((block, blockIndex) => (
                  <Text key={blockIndex} style={styles.timeBlock}>
                    {new Date(block.startTime).toLocaleTimeString()} - 
                    {new Date(block.endTime).toLocaleTimeString()}
                  </Text>
                ))}
              </View>

              <Button
                title="Schedule This Option"
                onPress={() => handleAcceptSchedule(decision.timeBlocks)}
                size="sm"
                style={styles.acceptButton}
              />
            </View>
          ))}
        </Card>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  description: {
    marginBottom: 20,
    textAlign: 'center',
  },
  confidence: {
    textAlign: 'right',
    fontStyle: 'italic',
    marginBottom: 10,
  },
  decision: {
    marginVertical: 10,
    padding: 10,
    backgroundColor: '#f9f9f9',
    borderRadius: 8,
  },
  optionTitle: {
    fontWeight: 'bold',
    marginBottom: 5,
  },
  timeBlocks: {
    marginVertical: 10,
  },
  timeBlock: {
    marginVertical: 2,
  },
  acceptButton: {
    marginTop: 10,
  },
}); 