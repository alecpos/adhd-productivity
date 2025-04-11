import { api } from '../../../lib/api';


export interface HyperfocusSessionStats {
    total_sessions: number;
    total_duration: number;
    average_duration: number;
    completion_rate: number;
}

export interface HyperfocusSession {
    id: string;
    user_id: string;
    task_id?: string;
    start_time: string;
    end_time?: string;
    duration_minutes: number;
    purpose?: string;
    environment?: string;
    tools_used?: string[];
    productivity_score?: number;
    focus_level?: number;
    status: 'active' | 'completed' | 'interrupted';
}

export interface StartSessionRequest {
    duration_minutes: number;
    purpose?: string;
    tools_used?: string[];
    focus_area?: string;
    task_id?: string;
}

export interface APIResponse<T> {
    data: T;
    message: string;
    status: 'success' | 'error';
}

export const HyperfocusService = {
    async startSession(data: StartSessionRequest): Promise<HyperfocusSession> {
        try {
            const response = await api.post<APIResponse<HyperfocusSession>>('/api/hyperfocus/session', data);
            return response.data.data;
        } catch (error) {
            console.error('Failed to start hyperfocus session:', error);
            throw error;
        }
    },

    async endSession(sessionId: string): Promise<HyperfocusSession> {
        try {
            const response = await api.post<APIResponse<HyperfocusSession>>(`/api/hyperfocus/session/${sessionId}/end`);
            return response.data.data;
        } catch (error) {
            console.error('Failed to end hyperfocus session:', error);
            throw error;
        }
    },

    async getSessionStats(): Promise<HyperfocusSessionStats> {
        try {
            const response = await api.get<APIResponse<HyperfocusSessionStats>>('/api/hyperfocus/statistics');
            return response.data.data;
        } catch (error) {
            console.error('Failed to fetch hyperfocus stats:', error);
            throw error;
        }
    },

    async getUserSessions(): Promise<HyperfocusSession[]> {
        try {
            const response = await api.get<APIResponse<HyperfocusSession[]>>('/api/hyperfocus/sessions');
            return response.data.data;
        } catch (error) {
            console.error('Failed to fetch hyperfocus sessions:', error);
            throw error;
        }
    },

    async logInterruption(sessionId: string, reason: string): Promise<void> {
        try {
            await api.post<APIResponse<void>>(`/api/hyperfocus/session/${sessionId}/interruption`, { reason });
        } catch (error) {
            console.error('Failed to log interruption:', error);
            throw error;
        }
    },

    async updateSession(sessionId: string, data: Partial<HyperfocusSession>): Promise<HyperfocusSession> {
        try {
            const response = await api.patch<APIResponse<HyperfocusSession>>(`/api/hyperfocus/session/${sessionId}`, data);
            return response.data.data;
        } catch (error) {
            console.error('Failed to update hyperfocus session:', error);
            throw error;
        }
    }
};
