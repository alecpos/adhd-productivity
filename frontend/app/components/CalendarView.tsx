import React, { useState, useEffect, useCallback, useMemo } from 'react';
import type { ReactElement } from 'react';

import { useTheme, Button, Icon } from '@rneui/themed';
import { format } from 'date-fns';
import { View, ScrollView, Text, ActivityIndicator } from 'react-native';
import { Calendar } from 'react-native-calendars';
import Toast from 'react-native-toast-message';

import { useAuth } from '../../contexts/AuthContext';
import { useCalendarService } from '../hooks/useCalendarService';

import type { AuthContextType as BaseAuthContextType } from '../types/auth';
import type { CalendarEvent } from '../types/calendar';
import type { DateData } from 'react-native-calendars';

// Local interfaces
interface Event {
  id: string;
  title: string;
  description?: string;
  startDate: string;
  endDate: string;
  source?: CalendarEvent['source'];
  sync_status?: CalendarEvent['status'];
}

interface SyncProgress {
  total: number;
  current: number;
  status: 'idle' | 'syncing' | 'error' | 'success';
}

type AuthContextType = Pick<BaseAuthContextType, 'user'>;

export default function CalendarView(): ReactElement {
  const auth = useAuth();
  const { user } = auth as unknown as AuthContextType;
  const calendarService = useCalendarService();
  const { theme } = useTheme();
  const [isSyncing, setIsSyncing] = useState(false);
  const [events, setEvents] = useState<Event[]>([]);
  const [selectedDate, setSelectedDate] = useState(format(new Date(), 'yyyy-MM-dd'));
  const [syncProgress, setSyncProgress] = useState<SyncProgress>({
    total: 0,
    current: 0,
    status: 'idle'
  });

  const fetchEvents = useCallback(async (): Promise<void> => {
    if (typeof user?.id !== 'string') return;
    try {
      const startDate = new Date(selectedDate);
      const fetchedEvents = await calendarService.getEvents(startDate);
      if (fetchedEvents) {
        setEvents(fetchedEvents.map(event => ({
          id: event.id ?? '',
          title: event.title ?? '',
          description: event.description,
          startDate: format(new Date(event.start_time ?? new Date()), 'yyyy-MM-dd\'T\'HH:mm:ss'),
          endDate: format(new Date(event.end_time ?? new Date()), 'yyyy-MM-dd\'T\'HH:mm:ss'),
          source: event.source ?? 'local',
          sync_status: event.status
        })));
      }
    } catch (_error) {
      Toast.show({
        type: 'error',
        text1: 'Error',
        text2: 'Failed to fetch events',
      });
    }
  }, [user?.id, calendarService, selectedDate]);

  const filteredEvents = useMemo(() => {
    return events.filter(event => 
      format(new Date(event.startDate), 'yyyy-MM-dd') === selectedDate
    );
  }, [events, selectedDate]);

  const handleSync = async (): Promise<void> => {
    if (typeof user?.id !== 'string') return;
    setIsSyncing(true);
    setSyncProgress({ total: 0, current: 0, status: 'syncing' });
    try {
      await calendarService.sync(user.id);
      setSyncProgress(prev => ({ ...prev, status: 'success' }));
      await fetchEvents();
      Toast.show({
        type: 'success',
        text1: 'Calendar Synced',
        text2: 'Your calendar has been updated with external events',
      });
    } catch (_error) {
      setSyncProgress(prev => ({ ...prev, status: 'error' }));
      Toast.show({
        type: 'error',
        text1: 'Sync Failed',
        text2: _error instanceof Error ? _error.message : 'Failed to sync calendar',
      });
    } finally {
      setIsSyncing(false);
      // Reset sync progress after a delay
      setTimeout(() => {
        setSyncProgress({ total: 0, current: 0, status: 'idle' });
      }, 3000);
    }
  };

  useEffect(() => {
    void fetchEvents();
  }, [fetchEvents]);

  const getSyncStatusStyle = (status: Event['sync_status']): { backgroundColor: string } => {
    switch (status) {
      case 'synced':
        return { backgroundColor: theme.colors.success };
      case 'pending':
        return { backgroundColor: theme.colors.warning };
      case 'failed':
        return { backgroundColor: theme.colors.error };
      default:
        return { backgroundColor: theme.colors.grey3 };
    }
  };

  const renderEvent = (event: Event): ReactElement => (
    <View key={event.id} style={styles.eventItem}>
      <View style={styles.eventHeader}>
        <Text style={styles.eventTitle}>{event.title}</Text>
        <View style={styles.eventMeta}>
          {event.source && (
            <View style={[styles.sourceTag, { backgroundColor: theme.colors.primary }]}>
              <Text style={styles.sourceText}>{event.source}</Text>
            </View>
          )}
          {event.sync_status && (
            <View style={[styles.syncStatus, getSyncStatusStyle(event.sync_status)]}>
              <Text style={styles.syncStatusText}>{event.sync_status}</Text>
            </View>
          )}
        </View>
      </View>
      {event.description && (
        <Text style={styles.eventDescription}>{event.description}</Text>
      )}
      <Text style={styles.eventTime}>
        {format(new Date(event.startDate), 'h:mm a')} - {format(new Date(event.endDate), 'h:mm a')}
      </Text>
    </View>
  );

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Calendar</Text>
        <View style={styles.headerRight}>
          {syncProgress.status !== 'idle' && (
            <View style={styles.syncProgress}>
              {syncProgress.status === 'syncing' && <ActivityIndicator size="small" color={theme.colors.primary} />}
              <Text style={styles.syncProgressText}>
                {syncProgress.status === 'syncing' ? 'Syncing...' :
                 syncProgress.status === 'success' ? 'Sync complete' :
                 syncProgress.status === 'error' ? 'Sync failed' : ''}
              </Text>
            </View>
          )}
          <Button
            icon={
              <Icon
                name="sync"
                type="material"
                size={20}
                color="white"
                style={{ marginRight: 10 }}
              />
            }
            title="Sync Calendar"
            onPress={handleSync}
            loading={isSyncing}
            disabled={isSyncing}
            containerStyle={styles.syncButton}
          />
        </View>
      </View>

      <Calendar
        current={selectedDate}
        onDayPress={(day: DateData) => setSelectedDate(day.dateString)}
        markedDates={{
          [selectedDate]: { selected: true, selectedColor: theme.colors.primary }
        }}
      />

      <View style={styles.eventsContainer}>
        <Text style={styles.eventsTitle}>Events</Text>
        <View style={styles.eventList}>
          {filteredEvents.length > 0 ? (
            filteredEvents.map(renderEvent)
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
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 15,
  },
  headerRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  syncButton: {
    minWidth: 140,
  },
  syncProgress: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
  },
  syncProgressText: {
    fontSize: 12,
    color: '#666',
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
    borderRadius: 8,
    gap: 8,
  },
  eventHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  eventMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
  },
  eventTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    flex: 1,
  },
  sourceTag: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  sourceText: {
    color: '#fff',
    fontSize: 12,
    textTransform: 'capitalize',
  },
  syncStatus: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  syncStatusText: {
    color: '#fff',
    fontSize: 12,
    textTransform: 'capitalize',
  },
  eventDescription: {
    color: '#666',
  },
  eventTime: {
    fontSize: 14,
    color: '#444',
  },
  noEventsText: {
    textAlign: 'center',
    color: '#666',
    marginTop: 20,
  },
} as const; 