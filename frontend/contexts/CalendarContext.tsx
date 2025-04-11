import React, { createContext, useContext, useState, useCallback } from 'react';

import { calendarService } from '../core/api/services/calendarService';

import { useAuth } from './AuthContext';

import type { CalendarEvent, CreateCalendarEvent, UpdateCalendarEvent } from '../core/api/services/calendarService';



interface CalendarContextType {
  events: CalendarEvent[];
  loading: boolean;
  error: string | null;
  fetchEvents: () => Promise<void>;
  createEvent: (eventData: CreateCalendarEvent) => Promise<void>;
  updateEvent: (eventId: string, eventData: UpdateCalendarEvent) => Promise<void>;
  deleteEvent: (eventId: string) => Promise<void>;
}

const CalendarContext = createContext<CalendarContextType | undefined>(undefined);

export function useCalendar() {
  const context = useContext(CalendarContext);
  if (!context) {
    throw new Error('useCalendar must be used within a CalendarProvider');
  }
  return context;
}

export function CalendarProvider({ children }: { children: React.ReactNode }) {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();

  const fetchEvents = useCallback(async () => {
    if (!user?.id) return;

    setLoading(true);
    setError(null);
    try {
      const fetchedEvents = await calendarService.getEvents(user.id);
      setEvents(fetchedEvents);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch events');
      console.error('Error fetching events:', err);
    } finally {
      setLoading(false);
    }
  }, [user?.id]);

  const createEvent = async (eventData: CreateCalendarEvent) => {
    if (!user?.id) return;

    setError(null);
    try {
      const newEvent = await calendarService.createEvent({
        ...eventData,
        user_id: user.id
      });
      setEvents(prev => [...prev, newEvent]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create event');
      throw err;
    }
  };

  const updateEvent = async (eventId: string, eventData: UpdateCalendarEvent) => {
    setError(null);
    try {
      const updatedEvent = await calendarService.updateEvent(eventId, eventData);
      setEvents(prev => prev.map(event =>
        event.id === eventId ? updatedEvent : event
      ));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update event');
      throw err;
    }
  };

  const deleteEvent = async (eventId: string) => {
    setError(null);
    try {
      await calendarService.deleteEvent(eventId);
      setEvents(prev => prev.filter(event => event.id !== eventId));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete event');
      throw err;
    }
  };

  return (
    <CalendarContext.Provider
      value={{
        events,
        loading,
        error,
        fetchEvents,
        createEvent,
        updateEvent,
        deleteEvent,
      }}
    >
      {children}
    </CalendarContext.Provider>
  );
}
