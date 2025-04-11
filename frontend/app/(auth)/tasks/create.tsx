import React, { useState, useEffect } from 'react';

import DateTimePicker from '@react-native-community/datetimepicker';
import { Picker } from '@react-native-picker/picker';
import { Input, useTheme, makeStyles, Button } from '@rneui/themed';
import { useRouter } from 'expo-router';
import { View, StyleSheet, Text, Platform, TouchableOpacity } from 'react-native';

import { useAuth } from 'contexts/AuthContext';


import { TaskAnalysis } from '../../../components/TaskAnalysis';
import { AnimatedButton } from '../../../components/ui/AnimatedButton';
import { FormField } from '../../components/ui/FormField';
import api from '../../services/api';

const RECURRENCE_OPTIONS = [
  { label: 'Daily', value: 'daily' },
  { label: 'Weekday', value: 'weekday' },
  { label: 'Weekly', value: 'weekly' },
  { label: 'Biweekly', value: 'biweekly' },
  { label: 'Monthly', value: 'monthly' },
  { label: 'Custom', value: 'custom' },
];

export default function CreateTaskScreen() {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [startDate, setStartDate] = useState(new Date());
  const [endDate, setEndDate] = useState(new Date());
  const [recurrenceType, setRecurrenceType] = useState('daily');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [taskType, setTaskType] = useState('');
  const [defaultCalendarId, setDefaultCalendarId] = useState<string | null>(null);
  const [showStartPicker, setShowStartPicker] = useState(false);
  const [showEndPicker, setShowEndPicker] = useState(false);
  const { user } = useAuth();
  const router = useRouter();
  const { theme } = useTheme();
  const styles = useStyles();

  useEffect(() => {
    // Fetch user's default calendar ID
    const fetchDefaultCalendar = async () => {
      try {
        const response = await api.get('/api/calendar/default');
        setDefaultCalendarId(response.data.id);
      } catch (err) {
        console.error('Failed to fetch default calendar:', err);
      }
    };

    if (user) {
      fetchDefaultCalendar();
    }
  }, [user]);

  const handleCreateTask = async () => {
    if (!title || !description) {
      setError('Title and description are required!');
      return;
    }

    setLoading(true);
    try {
      // Create calendar event
      const eventData = {
        title,
        description,
        start_time: startDate.toISOString(),
        end_time: endDate.toISOString(),
        user_id: user?.id,
        event_type: 'task',
        recurrence_type: recurrenceType,
        calendar_id: defaultCalendarId,
      };

      await api.post('/api/calendar/events', eventData);

      // Create task
      await api.post('/tasks', {
        title,
        description,
        due_date: endDate.toISOString(),
        type: taskType,
      });

      router.push('/(auth)/tasks' as any);
    } catch (error) {
      console.error('Failed to create task:', error);
      setError('Failed to create task. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const onStartDateChange = (event: any, selectedDate?: Date) => {
    setShowStartPicker(false);
    if (selectedDate) {
      setStartDate(selectedDate);
      if (selectedDate > endDate) {
        setEndDate(selectedDate);
      }
    }
  };

  const onEndDateChange = (event: any, selectedDate?: Date) => {
    setShowEndPicker(false);
    if (selectedDate) {
      setEndDate(selectedDate);
    }
  };

  if (!user) {
    throw new Error("User is null, but this shouldn't happen in authenticated routes.");
  }

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <Input
        label="Title"
        placeholder="Enter title"
        value={title}
        onChangeText={setTitle}
        errorMessage={error && !title ? error : ''}
        style={styles.input}
      />
      <Input
        label="Description"
        placeholder="Enter description"
        value={description}
        onChangeText={setDescription}
        errorMessage={error && !description ? error : ''}
        style={styles.input}
        multiline
        numberOfLines={3}
      />

      <View style={styles.dateSection}>
        <Text style={styles.sectionTitle}>Schedule</Text>

        <TouchableOpacity
          style={styles.dateButton}
          onPress={() => setShowStartPicker(true)}
        >
          <Text style={styles.dateButtonLabel}>Start Time</Text>
          <Text style={styles.dateButtonText}>
            {startDate.toLocaleString()}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.dateButton}
          onPress={() => setShowEndPicker(true)}
        >
          <Text style={styles.dateButtonLabel}>End Time</Text>
          <Text style={styles.dateButtonText}>
            {endDate.toLocaleString()}
          </Text>
        </TouchableOpacity>

        {showStartPicker && (
          <DateTimePicker
            value={startDate}
            mode="datetime"
            display="default"
            onChange={onStartDateChange}
          />
        )}

        {showEndPicker && (
          <DateTimePicker
            value={endDate}
            mode="datetime"
            display="default"
            onChange={onEndDateChange}
            minimumDate={startDate}
          />
        )}

        <View style={styles.recurrenceSection}>
          <Text style={styles.dateButtonLabel}>Repeats</Text>
          <Picker
            selectedValue={recurrenceType}
            onValueChange={setRecurrenceType}
            style={styles.picker}
          >
            {RECURRENCE_OPTIONS.map(option => (
              <Picker.Item
                key={option.value}
                label={option.label}
                value={option.value}
              />
            ))}
          </Picker>
        </View>
      </View>

      <FormField
        label="Task Type"
        value={taskType}
        onChangeText={setTaskType}
        placeholder="e.g., Focus, Creative, Administrative"
      />

      {description && taskType && (
        <TaskAnalysis
          taskDescription={description}
          taskType={taskType}
        />
      )}

      <AnimatedButton
        title={loading ? "Creating..." : "Create Task"}
        onPress={handleCreateTask}
        loading={loading}
        disabled={loading || !title || !description || !defaultCalendarId}
        containerStyle={styles.button}
        scaleOnPress
        pulseOnLoad
      />
    </View>
  );
}

const useStyles = makeStyles((theme) => ({
  container: {
    padding: theme.spacing.lg,
  },
  input: {
    marginBottom: theme.spacing.sm,
    borderColor: theme.colors.grey4,
    borderWidth: 1,
    borderRadius: theme.borderRadius.sm,
    padding: theme.spacing.sm,
  },
  dateSection: {
    marginBottom: theme.spacing.lg,
    backgroundColor: theme.colors.grey5,
    padding: theme.spacing.md,
    borderRadius: theme.borderRadius.md,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: theme.spacing.md,
    color: theme.colors.grey0,
  },
  dateButton: {
    backgroundColor: theme.colors.white,
    padding: theme.spacing.md,
    borderRadius: theme.borderRadius.sm,
    marginBottom: theme.spacing.sm,
  },
  dateButtonLabel: {
    fontSize: 14,
    color: theme.colors.grey2,
    marginBottom: 4,
  },
  dateButtonText: {
    fontSize: 16,
    color: theme.colors.grey0,
  },
  recurrenceSection: {
    marginTop: theme.spacing.sm,
  },
  picker: {
    backgroundColor: theme.colors.white,
    borderRadius: theme.borderRadius.sm,
    marginTop: 4,
  },
  button: {
    marginTop: theme.spacing.md,
    borderRadius: theme.borderRadius.sm,
    overflow: 'hidden',
  }
}));
