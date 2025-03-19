import { api } from '../../../lib/api';


export interface PomodoroSessionStats {
    total_sessions: number;
    total_duration: number;
    average_duration: number;
    completion_rate: number;
}

export interface PomodoroSession {
    id: string;
    user_id: string;
    task_id?: string;
    start_time: string;
    end_time?: string;
    focus_time: number;
    break_time: number;
    rounds: number;
    status: 'pending' | 'active' | 'paused' | 'completed' | 'cancelled';
    productivity_score?: number;
    focus_level?: number;
    notes?: string;
}

export interface StartSessionRequest {
    task_id?: string;
    focus_time?: number;
    break_time?: number;
    rounds?: number;
    notes?: string;
}

export interface APIResponse<T> {
    data: T;
    message: string;
    status: 'success' | 'error';
}

export const PomodoroService = {
    async startSession(data: StartSessionRequest): Promise<PomodoroSession> {
        try {
            const response = await api.post<APIResponse<PomodoroSession>>('/pomodoro/start', data);
            return response.data.data;
        } catch (error) {
            console.error('Failed to start pomodoro session:', error);
            throw new Error('Failed to start pomodoro session');
        }
    },

    async endSession(sessionId: string): Promise<PomodoroSession> {
        try {
            const response = await api.post<APIResponse<PomodoroSession>>(`/pomodoro/${sessionId}/end`);
            return response.data.data;
        } catch (error) {
            console.error('Failed to end pomodoro session:', error);
            throw new Error('Failed to end pomodoro session');
        }
    },

    async getSessionStats(): Promise<PomodoroSessionStats> {
        try {
            const response = await api.post<APIResponse<PomodoroSessionStats>>('/pomodoro/statistics');
            return response.data.data;
        } catch (error) {
            console.error('Failed to fetch pomodoro stats:', error);
            throw new Error('Failed to fetch pomodoro stats');
        }
    },

    async getUserSessions(): Promise<PomodoroSession[]> {
        try {
            const response = await api.post<APIResponse<PomodoroSession[]>>('/pomodoro/sessions');
            return response.data.data;
        } catch (error) {
            console.error('Failed to fetch pomodoro sessions:', error);
            throw new Error('Failed to fetch pomodoro sessions');
        }
    },

    async pauseSession(sessionId: string): Promise<PomodoroSession> {
        try {
            const response = await api.post<APIResponse<PomodoroSession>>(`/pomodoro/${sessionId}/pause`);
            return response.data.data;
        } catch (error) {
            console.error('Failed to pause pomodoro session:', error);
            throw new Error('Failed to pause pomodoro session');
        }
    },

    async resumeSession(sessionId: string): Promise<PomodoroSession> {
        try {
            const response = await api.post<APIResponse<PomodoroSession>>(`/pomodoro/${sessionId}/resume`);
            return response.data.data;
        } catch (error) {
            console.error('Failed to resume pomodoro session:', error);
            throw new Error('Failed to resume pomodoro session');
        }
    },

    async updateSession(sessionId: string, data: Partial<PomodoroSession>): Promise<PomodoroSession> {
        try {
            const response = await api.post<APIResponse<PomodoroSession>>(`/pomodoro/${sessionId}`, data);
            return response.data.data;
        } catch (error) {
            console.error('Failed to update pomodoro session:', error);
            throw new Error('Failed to update pomodoro session');
        }
    }
}; 