import React, { useState, useEffect, useCallback, memo } from 'react';
import { useMemo } from 'react';

import { useTheme } from '@rneui/themed';
import { format } from 'date-fns';
import { View, ScrollView, Text, TouchableOpacity, ActivityIndicator } from 'react-native';
import { Calendar } from 'react-native-calendars';


import { ErrorBoundary } from '@/app/components/ui/ErrorBoundary';
import { useCalendarService } from '@/app/hooks/useCalendarService';
import type { CalendarEvent } from '@/app/types/calendar';

import { useAuth } from '../contexts/AuthContext';

import type { DateData } from 'react-native-calendars';
import type { MarkedDates } from 'react-native-calendars/src/types';




const EventItem = memo(({ event, theme }: { event: CalendarEvent; theme: any }) => (
  <TouchableOpacity
    style={[
      styles.eventItem,
      { borderLeftColor: event.category === 'high_priority' ? '#d32f2f' : theme.colors.primary }
    ]}
  >
    <Text style={styles.eventTitle}>{event.title}</Text>
    <Text style={styles.eventTime}>
      {format(new Date(event.start_time), 'HH:mm')}
      {event.end_time && ` - ${format(new Date(event.end_time), 'HH:mm')}`}
    </Text>
  </TouchableOpacity>
));

const LoadingSpinner = () => (
  <View style={styles.loadingContainer}>
    <ActivityIndicator size="large" color="#0000ff" />
    <Text style={styles.loadingText}>Loading calendar...</Text>
  </View>
);

const ErrorDisplay = ({ error, onRetry }: { error: string; onRetry: () => void }) => (
  <View style={styles.errorContainer}>
    <Text style={styles.errorText}>{error}</Text>
    <TouchableOpacity style={styles.retryButton} onPress={onRetry}>
      <Text style={styles.retryButtonText}>Retry</Text>
    </TouchableOpacity>
  </View>
);

export default function CalendarView() {
  const { user } = useAuth();
  const calendarService = useCalendarService();
  const { theme } = useTheme();
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [markedDates, setMarkedDates] = useState<MarkedDates>({});

  const handleDateChange = useCallback((date: DateData) => {
    setSelectedDate(new Date(date.dateString));
  }, []);

  const fetchEvents = useCallback(async () => {
    setLoading(true);
    try {
      const events = await calendarService.getEvents(selectedDate) || [];
      setEvents(events);
      setError(null);
    } catch (err) {
      console.error("Failed to fetch events", err);
      setError(err instanceof Error ? err : new Error("Failed to fetch events"));
    } finally {
      setLoading(false);
    }
  }, [selectedDate, calendarService]);

  useEffect(() => {
    fetchEvents();
  }, [fetchEvents]);

  const handleRetry = useCallback(() => {
    setError(null);
    setLoading(true);
    fetchEvents().finally(() => setLoading(false));
  }, [fetchEvents]);

  const filteredEvents = useMemo(() =>
    events.filter(event =>
      format(new Date(event.start_time), 'yyyy-MM-dd') === format(selectedDate, 'yyyy-MM-dd')
    ),
    [events, selectedDate]
  );

  const calendarTheme = useMemo(() => ({
    calendarBackground: theme.colors.background,
    selectedDayBackgroundColor: theme.colors.primary,
    selectedDayTextColor: '#ffffff',
    todayTextColor: theme.colors.primary,
    dayTextColor: theme.colors.text,
    textDisabledColor: theme.colors.border,
    monthTextColor: theme.colors.text,
    textMonthFontWeight: 'bold',
    textDayFontSize: 16,
    textMonthFontSize: 18,
    textDayHeaderFontSize: 14
  }), [theme.colors]);

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <ErrorBoundary error={error} onRetry={fetchEvents} />;
  }

  return (
    <ScrollView style={styles.container}>
      <Calendar
        current={selectedDate.toISOString()}
        onDayPress={handleDateChange}
        markedDates={{
          [format(selectedDate, 'yyyy-MM-dd')]: {
            selected: true,
            selectedColor: theme.colors.primary,
            ...markedDates[format(selectedDate, 'yyyy-MM-dd')]
          },
          ...markedDates
        }}
        markingType="dot"
        theme={calendarTheme}
      />

      <View style={styles.eventsContainer}>
        <Text style={styles.eventsTitle}>Events</Text>
        <View style={styles.eventList}>
          {filteredEvents.length > 0 ? (
            filteredEvents.map((event) => (
              <EventItem key={event.id} event={event} theme={theme} />
            ))
          ) : (
            <Text style={styles.noEventsText}>No events for this day</Text>
          )}
        </View>
      </View>
    </ScrollView>
  );
}

const styles = {
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  loadingText: {
    marginTop: 10,
    color: '#666',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#fff',
  },
  errorText: {
    color: '#d32f2f',
    marginBottom: 10,
    textAlign: 'center',
  },
  retryButton: {
    backgroundColor: '#2196F3',
    padding: 10,
    borderRadius: 5,
  },
  retryButtonText: {
    color: '#fff',
  },
  eventsContainer: {
    padding: 15,
  },
  eventsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  eventList: {
    gap: 10,
  },
  eventItem: {
    backgroundColor: '#f5f5f5',
    padding: 15,
    borderRadius: 5,
    borderLeftWidth: 4,
  },
  eventTitle: {
    fontSize: 16,
    fontWeight: '500',
    marginBottom: 5,
  },
  eventTime: {
    fontSize: 14,
    color: '#666',
  },
  noEventsText: {
    textAlign: 'center',
    color: '#666',
    padding: 20,
  },
} as const;
