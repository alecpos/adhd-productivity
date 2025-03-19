import { useState, useCallback } from 'react';

import { calendarService } from '@/app/services/calendar';
import type { CalendarEvent, Reminder, CalendarSettings, TimeBlock, ScheduleStats } from '@/app/types/calendar';

import { useAuth } from '../../contexts/AuthContext';

interface CalendarServiceHook {
    loading: boolean;
    error: string | null;
    getEvents: (startDate?: Date, endDate?: Date, includeExternal?: boolean) => Promise<CalendarEvent[] | null>;
    createEvent: (event: Partial<CalendarEvent>) => Promise<string | null>;
    updateEvent: (eventId: string, updates: Partial<CalendarEvent>) => Promise<void | null>;
    deleteEvent: (eventId: string) => Promise<void | null>;
    getReminders: (reminderType?: string, includeDisabled?: boolean) => Promise<Reminder[] | null>;
    createReminder: (reminder: Partial<Reminder>) => Promise<string | null>;
    updateReminder: (reminderId: string, updates: Partial<Reminder>) => Promise<void | null>;
    deleteReminder: (reminderId: string) => Promise<void | null>;
    scheduleBlocks: (blocks: TimeBlock[]) => Promise<void | null>;
    getScheduleStats: () => Promise<ScheduleStats | null>;
    updateSettings: (settings: CalendarSettings) => Promise<void | null>;
    getSettings: () => Promise<CalendarSettings | null>;
    disconnectCalendar: () => Promise<void | null>;
    connectGoogle: (token: string) => Promise<boolean | null>;
    connectApple: () => Promise<boolean | null>;
    connectOutlook: () => Promise<boolean | null>;
    sync: (userId: string) => Promise<void | null>;
}

export function useCalendarService(): CalendarServiceHook {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const { user } = useAuth();

    const handleRequest = async <T>(request: () => Promise<T>): Promise<T | null> => {
        setLoading(true);
        setError(null);
        try {
            const result = await request();
            return result;
        } catch (err: unknown) {
            const errorMessage = err instanceof Error ? err.message : 'An error occurred';
            setError(errorMessage);
            return null;
        } finally {
            setLoading(false);
        }
    };

    const getEvents = useCallback(async (
        startDate?: Date,
        endDate?: Date,
        includeExternal: boolean = true
    ) => {
        if (!user?.id) return null;
        return handleRequest(() => calendarService.getCalendarEvents(
            user.id,
            startDate,
            endDate,
            includeExternal
        ));
    }, [user?.id]);

    const createEvent = useCallback(async (event: Partial<CalendarEvent>) => {
        return handleRequest(() => calendarService.createCalendarEvent(event));
    }, []);

    const updateEvent = useCallback(async (eventId: string, updates: Partial<CalendarEvent>) => {
        return handleRequest(() => calendarService.updateCalendarEvent(eventId, updates));
    }, []);

    const deleteEvent = useCallback(async (eventId: string) => {
        return handleRequest(() => calendarService.deleteCalendarEvent(eventId));
    }, []);

    const getReminders = useCallback(async (reminderType?: string, includeDisabled: boolean = false) => {
        if (!user?.id) return null;
        return handleRequest(() => calendarService.getReminders(user.id, reminderType ?? '', includeDisabled));
    }, [user?.id]);

    const createReminder = useCallback(async (reminder: Partial<Reminder>) => {
        return handleRequest(() => calendarService.createReminder(reminder));
    }, []);

    const updateReminder = useCallback(async (reminderId: string, updates: Partial<Reminder>) => {
        return handleRequest(() => calendarService.updateReminder(reminderId, updates));
    }, []);

    const deleteReminder = useCallback(async (reminderId: string) => {
        return handleRequest(() => calendarService.deleteReminder(reminderId));
    }, []);

    const scheduleBlocks = useCallback(async (blocks: TimeBlock[]) => {
        if (!user?.id) return null;
        return handleRequest(() => calendarService.scheduleBlocks(user.id, blocks));
    }, [user?.id]);

    const getScheduleStats = useCallback(async () => {
        if (!user?.id) return null;
        return handleRequest(() => calendarService.getScheduleStats(user.id));
    }, [user?.id]);

    const updateSettings = useCallback(async (settings: CalendarSettings) => {
        if (!user?.id) return null;
        return handleRequest(() => calendarService.updateCalendarSettings(user.id, settings));
    }, [user?.id]);

    const getSettings = useCallback(async () => {
        if (!user?.id) return null;
        return handleRequest(() => calendarService.getCalendarSettings(user.id));
    }, [user?.id]);

    const disconnectCalendar = useCallback(async () => {
        if (!user?.id) return null;
        return handleRequest(() => calendarService.disconnectCalendar(user.id));
    }, [user?.id]);

    // Provider-specific connection methods
    const connectGoogle = useCallback(async (token: string) => {
        return handleRequest(() => calendarService.setGoogleToken(token));
    }, []);

    const connectApple = useCallback(async () => {
        return handleRequest(() => calendarService.connectAppleCalendar());
    }, []);

    const connectOutlook = useCallback(async () => {
        return handleRequest(() => calendarService.connectOutlookCalendar());
    }, []);

    const sync = useCallback(async (userId: string) => {
        return handleRequest(() => calendarService.sync(userId));
    }, []);

    return {
        loading,
        error,
        getEvents,
        createEvent,
        updateEvent,
        deleteEvent,
        getReminders,
        createReminder,
        updateReminder,
        deleteReminder,
        scheduleBlocks,
        getScheduleStats,
        updateSettings,
        getSettings,
        disconnectCalendar,
        connectGoogle,
        connectApple,
        connectOutlook,
        sync
    };
} 