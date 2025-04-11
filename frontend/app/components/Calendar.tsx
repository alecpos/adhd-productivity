import React, { useState, useEffect } from 'react';

import { Text, makeStyles } from '@rneui/themed';
import { View } from 'react-native';
import { Calendar as RNCalendar } from 'react-native-calendars';

import { TaskCreate } from './TaskCreate';


export function Calendar() {
  const [selectedDate, setSelectedDate] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [selectedDateTime, setSelectedDateTime] = useState<Date | undefined>();
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

  if (isOffline) {
    return (
      <View style={styles.container}>
        <Text h4>Calendar</Text>
        <View style={styles.offlineMessage}>
          <Text style={styles.offlineText}>
            You are currently offline. Calendar features will be limited.
          </Text>
          <Text style={styles.offlineSubtext}>
            Connect to the internet to access all features.
          </Text>
        </View>
        <RNCalendar
          onDayPress={day => {
            setSelectedDate(day.dateString);
            setShowModal(true);
            setSelectedDateTime(new Date(day.dateString));
          }}
          markedDates={{
            [selectedDate]: { selected: true, selectedColor: '#2089dc' }
          }}
          theme={{
            todayTextColor: '#2089dc',
            selectedDayBackgroundColor: '#2089dc',
            selectedDayTextColor: '#ffffff',
          }}
        />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text h4>Calendar</Text>
      <RNCalendar
        onDayPress={day => {
          setSelectedDate(day.dateString);
          setShowModal(true);
          setSelectedDateTime(new Date(day.dateString));
        }}
        markedDates={{
          [selectedDate]: { selected: true, selectedColor: '#2089dc' }
        }}
        theme={{
          todayTextColor: '#2089dc',
          selectedDayBackgroundColor: '#2089dc',
          selectedDayTextColor: '#ffffff',
        }}
      />

      <TaskCreate
        visible={showModal}
        onClose={() => setShowModal(false)}
        initialDate={selectedDateTime}
      />
    </View>
  );
}

const useStyles = makeStyles((theme) => ({
  container: {
    flex: 1,
    padding: theme.spacing.md,
  },
  offlineMessage: {
    backgroundColor: theme.colors.warning,
    padding: theme.spacing.md,
    borderRadius: theme.borderRadius.sm,
    marginVertical: theme.spacing.md,
  },
  offlineText: {
    color: theme.colors.white,
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: theme.spacing.xs,
  },
  offlineSubtext: {
    color: theme.colors.white,
    fontSize: 14,
  },
}));
