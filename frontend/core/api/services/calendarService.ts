import { API_ENDPOINTS } from '../../../core/config';
import { api } from '../../../lib/api';

import type { UUID } from '../../../types/common';

export interface CalendarEvent {
    id: UUID;
    user_id: UUID;
    title: string;
    description?: string;
    start_time: string;
    end_time: string;
    created_at: string;
    updated_at: string;
    sync_status?: 'pending' | 'synced' | 'failed';
    external_id?: string;
    recurrence?: string;
    all_day?: boolean;
    location?: string;
    color?: string;
}

export interface CreateCalendarEvent {
    user_id: UUID;
    title: string;
    description?: string;
    start_time: string;
    end_time: string;
    event_type: "task" | "meeting" | "break" | "focus" | "social" | "other";
    recurrence_type: "none" | "daily" | "weekly" | "monthly" | "yearly" | "custom";
    all_day?: boolean;
    location?: string;
    color?: string;
}

export interface UpdateCalendarEvent {
    title?: string;
    description?: string;
    start_time?: string;
    end_time?: string;
    recurrence?: string;
    all_day?: boolean;
    location?: string;
    color?: string;
    sync_status?: 'pending' | 'synced' | 'failed';
}

export interface CalendarSettings {
    default_view: 'day' | 'week' | 'month';
    start_of_week: 0 | 1 | 2 | 3 | 4 | 5 | 6;
    working_hours: {
        start: string;
        end: string;
    };
    time_zone: string;
    notifications_enabled: boolean;
}

class CalendarService {
    async getEvents(userId: UUID, startDate?: string, endDate?: string): Promise<CalendarEvent[]> {
        const params = new URLSearchParams();
        if (startDate) params.append('start_date', new Date(startDate).toISOString());
        if (endDate) params.append('end_date', new Date(endDate).toISOString());
        
        const response = await api.get<CalendarEvent[]>(`${API_ENDPOINTS.CALENDAR.USER_EVENTS(userId)}?${params.toString()}`);
        return response.data;
    }

    async createEvent(eventData: CreateCalendarEvent): Promise<CalendarEvent> {
        const response = await api.post<CalendarEvent>(API_ENDPOINTS.CALENDAR.EVENTS, eventData);
        return response.data;
    }

    async updateEvent(eventId: UUID, eventData: UpdateCalendarEvent): Promise<CalendarEvent> {
        const response = await api.put<CalendarEvent>(API_ENDPOINTS.CALENDAR.EVENT(eventId), eventData);
        return response.data;
    }

    async deleteEvent(eventId: UUID): Promise<void> {
        await api.delete(API_ENDPOINTS.CALENDAR.EVENT(eventId));
    }

    async getSettings(userId: UUID): Promise<CalendarSettings> {
        const response = await api.get<CalendarSettings>(API_ENDPOINTS.CALENDAR.SETTINGS(userId));
        return response.data;
    }

    async updateSettings(userId: UUID, settings: Partial<CalendarSettings>): Promise<CalendarSettings> {
        const response = await api.put<CalendarSettings>(API_ENDPOINTS.CALENDAR.SETTINGS(userId), settings);
        return response.data;
    }

    async syncEvents(userId: UUID): Promise<void> {
        await api.post(API_ENDPOINTS.CALENDAR.SYNC(userId));
    }

    async getAvailableSlots(userId: UUID, duration: number, startDate: string, endDate: string): Promise<string[]> {
        const params = new URLSearchParams({
            duration: duration.toString(),
            start_date: startDate,
            end_date: endDate
        });
        
        const response = await api.get<string[]>(`${API_ENDPOINTS.CALENDAR.AVAILABLE_SLOTS(userId)}?${params.toString()}`);
        return response.data;
    }
}

export const calendarService = new CalendarService();