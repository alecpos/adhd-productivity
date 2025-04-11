export enum EventType {
    TASK = 'task',
    MEETING = 'meeting',
    REMINDER = 'reminder',
    BREAK = 'break',
    FOCUS = 'focus',
    OTHER = 'other'
}

export enum RecurrenceType {
    NONE = 'none',
    DAILY = 'daily',
    WEEKLY = 'weekly',
    MONTHLY = 'monthly',
    YEARLY = 'yearly',
    CUSTOM = 'custom'
}

export interface CalendarEvent {
    id?: string;
    user_id?: string;
    title: string;
    description?: string;
    start_time: string | Date;
    end_time: string | Date;
    event_type: EventType;
    is_all_day: boolean;
    location?: string;
    recurrence_type: RecurrenceType;
    recurrence_end?: string | Date;
    meta_data?: Record<string, any>;
    created_at?: string;
    updated_at?: string;
    source?: 'local' | 'google' | 'outlook' | 'apple';
    status?: 'pending' | 'synced' | 'failed';
}

export interface Reminder {
    id?: string;
    user_id?: string;
    title: string;
    description?: string;
    trigger_time: string | Date;
    event_id?: string;
    is_recurring: boolean;
    recurrence_type?: RecurrenceType;
    recurrence_end?: string | Date;
    notification_type: 'email' | 'push' | 'both';
    status: 'pending' | 'sent' | 'failed';
    created_at?: string;
    updated_at?: string;
}

export interface CalendarSettings {
    user_id: string;
    default_view: 'day' | 'week' | 'month';
    start_of_week: 0 | 1 | 6; // 0 = Sunday, 1 = Monday, 6 = Saturday
    working_hours: {
        start: string;
        end: string;
    };
    time_zone: string;
    notification_preferences: {
        email: boolean;
        push: boolean;
        default_reminder_minutes: number;
    };
    created_at?: string;
    updated_at?: string;
}

export interface TimeBlock {
    id?: string;
    user_id?: string;
    title: string;
    description?: string;
    start_time: string | Date;
    end_time: string | Date;
    block_type: 'focus' | 'break' | 'meeting';
    energy_level?: number;
    productivity_score?: number;
    is_completed: boolean;
    meta_data?: Record<string, any>;
    created_at?: string;
    updated_at?: string;
}

export interface ScheduleBlock {
    id?: string;
    user_id?: string;
    title: string;
    description?: string;
    start_time: string | Date;
    end_time: string | Date;
    block_type: 'focus' | 'break' | 'meeting';
    is_flexible: boolean;
    priority: number;
    energy_requirement: number;
    meta_data?: Record<string, any>;
    created_at?: string;
    updated_at?: string;
}

export interface ScheduleStats {
    user_id: string;
    period_start: string | Date;
    period_end: string | Date;
    total_focus_time: number;
    total_break_time: number;
    completed_blocks: number;
    missed_blocks: number;
    average_productivity: number;
    energy_level_distribution: Record<number, number>;
    most_productive_times: Array<{
        hour: number;
        productivity: number;
    }>;
    created_at?: string;
    updated_at?: string;
}

export interface SchedulingRequest {
    user_id: string;
    title: string;
    description?: string;
    duration_minutes: number;
    preferred_start_time?: string | Date;
    preferred_end_time?: string | Date;
    required_energy_level?: number;
    priority: number;
    is_flexible: boolean;
    block_type: 'focus' | 'break' | 'meeting';
    meta_data?: Record<string, any>;
}

export interface SchedulingSuggestion {
    id?: string;
    request_id: string;
    suggested_blocks: TimeBlock[];
    confidence_score: number;
    reasoning: string;
    alternative_slots?: Array<{
        start_time: string | Date;
        end_time: string | Date;
        confidence_score: number;
    }>;
    meta_data?: Record<string, any>;
    created_at?: string;
    updated_at?: string;
}
