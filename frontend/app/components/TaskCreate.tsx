import React, { useState, useEffect } from 'react';

import DateTimePicker from '@react-native-community/datetimepicker';
import { Picker } from '@react-native-picker/picker';
import { Text, Input, Button, makeStyles } from '@rneui/themed';
import { View, TouchableOpacity, Modal, Platform } from 'react-native';

import { useAuth } from '../../contexts/AuthContext';
import { api } from '../../services/api';

const RECURRENCE_OPTIONS = [
  { label: 'Daily', value: 'daily' },
  { label: 'Weekday', value: 'weekday' },
  { label: 'Weekly', value: 'weekly' },
  { label: 'Biweekly', value: 'biweekly' },
  { label: 'Monthly', value: 'monthly' },
  { label: 'Custom', value: 'custom' },
];

interface TaskCreateProps {
  visible: boolean;
  onClose: () => void;
  initialDate?: Date;
}

export function TaskCreate({ visible, onClose, initialDate }: TaskCreateProps) {
  const { user } = useAuth();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [startDate, setStartDate] = useState(new Date());
  const [endDate, setEndDate] = useState(new Date());
  const [recurrenceType, setRecurrenceType] = useState('daily');
  const [showStartPicker, setShowStartPicker] = useState(false);
  const [showEndPicker, setShowEndPicker] = useState(false);
  const [defaultCalendarId, setDefaultCalendarId] = useState<string | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [isOffline, setIsOffline] = useState(!navigator.onLine);
  const styles = useStyles();

  useEffect(() => {
    const handleOnline = () => setIsOffline(false);
    const handleOffline = () => setIsOffline(true);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Only fetch default calendar once when component mounts and when online
  useEffect(() => {
    let mounted = true;
    
    const fetchDefaultCalendar = async () => {
      if (isOffline) {
        // Use a temporary ID when offline
        setDefaultCalendarId('offline_calendar');
        return;
      }

      try {
        const response = await api.get('/api/calendar/default');
        if (mounted && response.data?.id) {
          setDefaultCalendarId(response.data.id);
        }
      } catch (err) {
        console.error('Failed to fetch default calendar:', err);
        // For development or offline, set a temporary default calendar ID
        if (mounted) {
          setDefaultCalendarId('temp_calendar_id');
        }
      }
    };
    
    if (user) {
      fetchDefaultCalendar();
    }

    return () => {
      mounted = false;
    };
  }, [user, isOffline]);

  // Update dates when initialDate changes
  useEffect(() => {
    if (initialDate) {
      const date = new Date(initialDate);
      if (!isNaN(date.getTime())) {
        setStartDate(date);
        setEndDate(date);
      }
    }
  }, [initialDate]);

  const handleCreateTask = async () => {
    if (!title || !description) {
      setError('Title and description are required!');
      return;
    }

    setLoading(true);
    try {
      const eventData = {
        title,
        description,
        start_time: startDate instanceof Date ? startDate.toISOString() : new Date(startDate).toISOString(),
        end_time: endDate instanceof Date ? endDate.toISOString() : new Date(endDate).toISOString(),
        user_id: user?.id,
        event_type: 'task',
        recurrence_type: recurrenceType,
        calendar_id: defaultCalendarId,
      };

      if (isOffline) {
        // Store task locally when offline
        const offlineTasks = JSON.parse(localStorage.getItem('offlineTasks') || '[]');
        offlineTasks.push({
          ...eventData,
          id: `offline_${Date.now()}`,
          created_at: new Date().toISOString(),
          synced: false
        });
        localStorage.setItem('offlineTasks', JSON.stringify(offlineTasks));
      } else {
        await api.post('/api/calendar/events', eventData);
      }

      resetForm();
      onClose();
    } catch (error) {
      console.error('Failed to create task:', error);
      if (isOffline) {
        setError('Task saved offline. It will sync when you reconnect.');
      } else {
        setError('Failed to create task. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setTitle('');
    setDescription('');
    setStartDate(initialDate ? new Date(initialDate) : new Date());
    setEndDate(initialDate ? new Date(initialDate) : new Date());
    setRecurrenceType('daily');
    setError('');
  };

  const onStartDateChange = (event: any, selectedDate?: Date) => {
    setShowStartPicker(Platform.OS === 'ios' ? true : false);
    if (selectedDate && !isNaN(selectedDate.getTime())) {
      setStartDate(selectedDate);
      if (selectedDate > endDate) {
        setEndDate(selectedDate);
      }
    }
  };

  const onEndDateChange = (event: any, selectedDate?: Date) => {
    setShowEndPicker(Platform.OS === 'ios' ? true : false);
    if (selectedDate && !isNaN(selectedDate.getTime())) {
      setEndDate(selectedDate);
    }
  };

  const renderDateTimePicker = () => {
    if (Platform.OS === 'web') {
      return (
        <>
          <View style={styles.webDatePickerContainer}>
            <Text style={styles.dateButtonLabel}>Start Time</Text>
            <input
              type="datetime-local"
              value={startDate instanceof Date ? startDate.toISOString().slice(0, 16) : new Date(startDate).toISOString().slice(0, 16)}
              onChange={(e) => {
                const date = new Date(e.target.value);
                if (!isNaN(date.getTime())) {
                  setStartDate(date);
                  if (date > endDate) {
                    setEndDate(date);
                  }
                }
              }}
              style={styles.webDatePicker}
            />
          </View>
          <View style={styles.webDatePickerContainer}>
            <Text style={styles.dateButtonLabel}>End Time</Text>
            <input
              type="datetime-local"
              value={endDate instanceof Date ? endDate.toISOString().slice(0, 16) : new Date(endDate).toISOString().slice(0, 16)}
              onChange={(e) => {
                const date = new Date(e.target.value);
                if (!isNaN(date.getTime())) {
                  setEndDate(date);
                }
              }}
              min={startDate instanceof Date ? startDate.toISOString().slice(0, 16) : new Date(startDate).toISOString().slice(0, 16)}
              style={styles.webDatePicker}
            />
          </View>
        </>
      );
    }

    return (
      <>
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
            testID="startDatePicker"
            value={startDate}
            mode="datetime"
            display={Platform.OS === 'ios' ? 'spinner' : 'default'}
            onChange={onStartDateChange}
          />
        )}

        {showEndPicker && (
          <DateTimePicker
            testID="endDatePicker"
            value={endDate}
            mode="datetime"
            display={Platform.OS === 'ios' ? 'spinner' : 'default'}
            onChange={onEndDateChange}
            minimumDate={startDate}
          />
        )}
      </>
    );
  };

  return (
    <Modal
      visible={visible}
      animationType="slide"
      transparent={true}
      onRequestClose={() => {
        resetForm();
        onClose();
      }}
    >
      <View style={styles.modalContainer}>
        <View style={styles.modalContent}>
          <Text h4 style={styles.modalTitle}>Add Task</Text>
          
          <Input
            label="Title"
            placeholder="Enter title"
            value={title}
            onChangeText={setTitle}
            errorMessage={error && !title ? error : ''}
          />
          
          <Input
            label="Description"
            placeholder="Enter description"
            value={description}
            onChangeText={setDescription}
            errorMessage={error && !description ? error : ''}
            multiline
            numberOfLines={3}
          />

          <View style={styles.dateSection}>
            <Text style={styles.sectionTitle}>Schedule</Text>
            
            {renderDateTimePicker()}

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

          <View style={styles.buttonContainer}>
            <Button
              title="Cancel"
              onPress={() => {
                resetForm();
                onClose();
              }}
              type="outline"
              containerStyle={styles.button}
            />
            <Button
              title={loading ? "Creating..." : "Create Task"}
              onPress={handleCreateTask}
              loading={loading}
              disabled={loading || !title || !description || !defaultCalendarId}
              containerStyle={styles.button}
            />
          </View>
        </View>
      </View>
    </Modal>
  );
}

const useStyles = makeStyles((theme) => ({
  modalContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },
  modalContent: {
    backgroundColor: theme.colors.background,
    padding: theme.spacing.lg,
    borderRadius: theme.borderRadius.md,
    width: '90%',
    maxHeight: '80%',
  },
  modalTitle: {
    textAlign: 'center',
    marginBottom: theme.spacing.md,
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
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: theme.spacing.md,
  },
  button: {
    flex: 1,
    marginHorizontal: theme.spacing.xs,
  },
  iosDatePicker: {
    width: '100%',
    backgroundColor: theme.colors.white,
    marginBottom: theme.spacing.sm,
    borderRadius: theme.borderRadius.sm,
  },
  webDatePickerContainer: {
    marginBottom: theme.spacing.md,
  },
  webDatePicker: {
    width: '100%',
    padding: theme.spacing.sm,
    borderRadius: theme.borderRadius.sm,
    borderColor: theme.colors.grey3,
    borderWidth: 1,
    marginTop: 4,
  },
})); 