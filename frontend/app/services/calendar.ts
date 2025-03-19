import * as AppleAuthentication from 'expo-apple-authentication';
import { makeRedirectUri } from 'expo-auth-session';
import * as WebBrowser from 'expo-web-browser';
import { Platform } from 'react-native';

import api from './api';

import type { 
    CalendarEvent, 
    Reminder, 
    CalendarSettings,
    TimeBlock,
    ScheduleStats,
    SchedulingRequest,
    SchedulingSuggestion
} from '../types/calendar';

interface OutlookTokenResponse {
    access_token: string;
}

interface WebBrowserResult {
    type: string;
    url?: string;
}

WebBrowser.maybeCompleteAuthSession();

export interface Task {
    id: string;
    title: string;
    description?: string;
    startTime: Date;
    endTime: Date;
    difficulty: number;
    energyRequired: number;
    subtasks: SubTask[];
    completed: boolean;
    recurring?: boolean;
    reminders: string[];
    color?: string;
    userId: string;
}

export interface SubTask {
    id: string;
    title: string;
    completed: boolean;
    estimatedDuration: number;
}

class CalendarService {
    private static instance: CalendarService;
    private currentProvider?: 'google' | 'apple' | 'outlook';
    private accessToken?: string;

    private constructor() {}

    static getInstance(): CalendarService {
        if (CalendarService.instance === undefined) {
            CalendarService.instance = new CalendarService();
        }
        return CalendarService.instance;
    }

    // Provider status methods
    getCurrentProvider(): string | undefined {
        return this.currentProvider;
    }

    isConnected(): boolean {
        return this.currentProvider !== undefined && this.accessToken !== undefined;
    }

    // Provider Authentication
    async setGoogleToken(token: string): Promise<boolean> {
        try {
            await api.post('/calendar/settings', {
                provider: 'google',
                settings: { access_token: token }
            });
            this.currentProvider = 'google';
            this.accessToken = token;
            return true;
        } catch (error) {
            console.error('Error setting Google token:', error);
            throw error;
        }
    }

    async connectAppleCalendar(): Promise<boolean> {
        if (Platform.OS !== 'ios') {
            return false;
        }

        try {
            const credential = await AppleAuthentication.signInAsync({
                requestedScopes: [
                    AppleAuthentication.AppleAuthenticationScope.FULL_NAME,
                    AppleAuthentication.AppleAuthenticationScope.EMAIL
                ]
            });

            if (!credential.identityToken) {
                throw new Error('Token exchange failed');
            }

            // Disconnect any existing calendar first
            await this.disconnectCalendar('test-user').catch(() => {
                // Ignore disconnection errors during connection
            });

            // Update calendar settings with Apple credentials
            await api.post('/calendar/settings', {
                provider: 'apple',
                settings: {
                    identity_token: credential.identityToken,
                    user_id: credential.user
                }
            });

            this.currentProvider = 'apple';
            this.accessToken = credential.identityToken;
            return true;
        } catch (error) {
            console.error('Error connecting Apple Calendar:', error);
            this.currentProvider = undefined;
            this.accessToken = undefined;
            throw error;
        }
    }

    async connectOutlookCalendar(): Promise<boolean> {
        try {
            const redirectUri = makeRedirectUri({
                scheme: 'adhd-calendar',
                path: 'outlook-auth'
            });

            const authUrl = `https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id=${process.env.EXPO_PUBLIC_MICROSOFT_CLIENT_ID}&response_type=code&redirect_uri=${encodeURIComponent(redirectUri)}&scope=calendars.read calendars.readwrite`;

            const result = await WebBrowser.openAuthSessionAsync(authUrl, redirectUri) as WebBrowserResult;

            if (result.type === 'success' && typeof result.url === 'string') {
                const code = new URL(result.url).searchParams.get('code');
                if (code) {
                    const response = await api.post<OutlookTokenResponse>('/calendar/outlook/token', { code, redirectUri });
                    const { access_token } = response.data;

                    this.currentProvider = 'outlook';
                    this.accessToken = access_token;
                    await api.post('/calendar/settings', {
                        provider: 'outlook',
                        settings: { access_token }
                    });
                    return true;
                }
            }
            return false;
        } catch (error) {
            console.error('Error connecting Outlook Calendar:', error);
            throw error;
        }
    }

    // Calendar Event Management
    async getCalendarEvents(
        userId: string,
        startDate?: Date,
        endDate?: Date,
        includeExternal: boolean = true
    ): Promise<CalendarEvent[]> {
        try {
            const response = await api.get<CalendarEvent[]>('/calendar/events', {
                params: { 
                    user_id: userId,
                    start_date: startDate?.toISOString(),
                    end_date: endDate?.toISOString(),
                    include_external: includeExternal 
                }
            });
            return response.data;
        } catch (error) {
            console.error('Failed to fetch calendar events', error);
            throw new Error('Failed to fetch events');
        }
    }

    async createCalendarEvent(event: Partial<CalendarEvent>): Promise<string> {
        try {
            const response = await api.post<{ event_id: string }>('/calendar/events', {
                ...event,
                start_time: event.start_time instanceof Date ? event.start_time.toISOString() : event.start_time,
                end_time: event.end_time instanceof Date ? event.end_time.toISOString() : event.end_time,
                recurrence_end: event.recurrence_end instanceof Date ? event.recurrence_end.toISOString() : event.recurrence_end,
                user_id: event.user_id,
                event_type: event.event_type,
                is_all_day: event.is_all_day,
                recurrence_type: event.recurrence_type,
                meta_data: event.meta_data
            });
            return response.data.event_id;
        } catch (error) {
            console.error('Error creating calendar event:', error);
            throw error;
        }
    }

    async updateCalendarEvent(
        eventId: string,
        updates: Partial<CalendarEvent>
    ): Promise<void> {
        try {
            await api.put(`/calendar/events/${eventId}`, {
                ...updates,
                start_time: updates.start_time instanceof Date ? updates.start_time.toISOString() : updates.start_time,
                end_time: updates.end_time instanceof Date ? updates.end_time.toISOString() : updates.end_time,
                recurrence_end: updates.recurrence_end instanceof Date ? updates.recurrence_end.toISOString() : updates.recurrence_end,
                user_id: updates.user_id,
                event_type: updates.event_type,
                is_all_day: updates.is_all_day,
                recurrence_type: updates.recurrence_type,
                meta_data: updates.meta_data
            });
        } catch (error) {
            console.error('Error updating calendar event:', error);
            throw error;
        }
    }

    async deleteCalendarEvent(eventId: string): Promise<void> {
        try {
            await api.delete(`/calendar/events/${eventId}`);
        } catch (error) {
            console.error('Error deleting calendar event:', error);
            throw error;
        }
    }

    // Reminder Management
    async getReminders(
        userId: string,
        reminderType?: string,
        includeDisabled: boolean = false
    ): Promise<Reminder[]> {
        try {
            const response = await api.get<Reminder[]>('/calendar/reminders', {
                params: {
                    user_id: userId,
                    reminder_type: reminderType,
                    include_disabled: includeDisabled
                }
            });
            return response.data;
        } catch (error) {
            console.error('Error fetching reminders:', error);
            throw error;
        }
    }

    async createReminder(reminder: Partial<Reminder>): Promise<string> {
        try {
            const response = await api.post<{ reminder_id: string }>('/calendar/reminders', {
                ...reminder,
                trigger_time: reminder.trigger_time instanceof Date ? reminder.trigger_time.toISOString() : reminder.trigger_time,
                recurrence_end: reminder.recurrence_end instanceof Date ? reminder.recurrence_end.toISOString() : reminder.recurrence_end,
                user_id: reminder.user_id,
                title: reminder.title,
                description: reminder.description,
                event_id: reminder.event_id,
                is_recurring: reminder.is_recurring,
                recurrence_type: reminder.recurrence_type,
                notification_type: reminder.notification_type,
                status: reminder.status
            });
            return response.data.reminder_id;
        } catch (error) {
            console.error('Error creating reminder:', error);
            throw error;
        }
    }

    async updateReminder(
        reminderId: string,
        updates: Partial<Reminder>
    ): Promise<void> {
        try {
            await api.put(`/calendar/reminders/${reminderId}`, {
                ...updates,
                trigger_time: updates.trigger_time instanceof Date ? updates.trigger_time.toISOString() : updates.trigger_time,
                recurrence_end: updates.recurrence_end instanceof Date ? updates.recurrence_end.toISOString() : updates.recurrence_end,
                user_id: updates.user_id,
                title: updates.title,
                description: updates.description,
                event_id: updates.event_id,
                is_recurring: updates.is_recurring,
                recurrence_type: updates.recurrence_type,
                notification_type: updates.notification_type,
                status: updates.status
            });
        } catch (error) {
            console.error('Error updating reminder:', error);
            throw error;
        }
    }

    async deleteReminder(reminderId: string): Promise<void> {
        try {
            await api.delete(`/calendar/reminders/${reminderId}`);
        } catch (error) {
            console.error('Error deleting reminder:', error);
            throw error;
        }
    }

    // Block Scheduling
    async scheduleBlocks(userId: string, blocks: TimeBlock[]): Promise<void> {
        try {
            await api.post('/calendar/schedule-blocks', { 
                user_id: userId,
                blocks: blocks.map(block => ({
                    ...block,
                    start_time: block.start_time instanceof Date ? block.start_time.toISOString() : block.start_time,
                    end_time: block.end_time instanceof Date ? block.end_time.toISOString() : block.end_time,
                    block_type: block.block_type,
                    energy_level: block.energy_level,
                    productivity_score: block.productivity_score,
                    is_completed: block.is_completed,
                    meta_data: block.meta_data
                }))
            });
        } catch (error) {
            console.error('Error scheduling blocks:', error);
            throw error;
        }
    }

    async getScheduleStats(userId: string): Promise<ScheduleStats> {
        try {
            const response = await api.get<ScheduleStats>('/calendar/schedule-stats', {
                params: { user_id: userId }
            });
            return response.data;
        } catch (error) {
            console.error('Error getting schedule stats:', error);
            throw error;
        }
    }

    async getScheduleSuggestions(request: SchedulingRequest): Promise<SchedulingSuggestion[]> {
        try {
            const response = await api.post<SchedulingSuggestion[]>('/calendar/schedule-suggestions', {
                ...request,
                user_id: request.user_id,
                title: request.title,
                description: request.description,
                duration_minutes: request.duration_minutes,
                preferred_start_time: request.preferred_start_time instanceof Date ? request.preferred_start_time.toISOString() : request.preferred_start_time,
                preferred_end_time: request.preferred_end_time instanceof Date ? request.preferred_end_time.toISOString() : request.preferred_end_time,
                required_energy_level: request.required_energy_level,
                priority: request.priority,
                is_flexible: request.is_flexible,
                block_type: request.block_type,
                meta_data: request.meta_data
            });
            return response.data;
        } catch (error) {
            console.error('Error getting schedule suggestions:', error);
            throw error;
        }
    }

    async updateCalendarSettings(userId: string, settings: Partial<CalendarSettings>): Promise<void> {
        try {
            await api.put('/calendar/settings', {
                user_id: userId,
                ...settings
            });
        } catch (error) {
            console.error('Error updating calendar settings:', error);
            throw error;
        }
    }

    async getCalendarSettings(userId: string): Promise<CalendarSettings> {
        try {
            const response = await api.get<CalendarSettings>('/calendar/settings', {
                params: { user_id: userId }
            });
            return response.data;
        } catch (error) {
            console.error('Error getting calendar settings:', error);
            throw error;
        }
    }

    async disconnectCalendar(userId: string): Promise<void> {
        try {
            await api.post('/calendar/disconnect', { user_id: userId });
            this.currentProvider = undefined;
            this.accessToken = undefined;
        } catch (error) {
            console.error('Error disconnecting calendar:', error);
            throw error;
        }
    }

    async sync(userId: string): Promise<void> {
        try {
            if (!this.currentProvider) {
                throw new Error('No calendar provider connected');
            }
            await api.post('/calendar/sync', { user_id: userId });
        } catch (error) {
            console.error('Error syncing calendar:', error);
            throw error;
        }
    }
}

export const calendarService = CalendarService.getInstance();
export default CalendarService; 