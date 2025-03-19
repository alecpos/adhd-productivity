import { api } from '@/lib/api';

import { AppError } from '../../core/errors';

import type { ApiResponse } from '../../types/common';

export interface HyperfocusSession {
  id: string;
  user_id: string;
  start_time: string;
  end_time?: string;
  duration?: number;
  task_id?: string;
  notes?: string;
  rating?: number;
  task_type?: string; // Make optional since it might not exist in DB
  status: 'active' | 'completed' | 'cancelled';
}

export interface SessionStats {
  total_sessions: number;
  total_duration: number;
  average_duration: number;
  completion_rate: number;
  average_rating: number;
  most_productive_time?: string;
  streak_days: number;
}

export class HyperfocusService {
  async startSession(taskId?: string, taskType?: string): Promise<HyperfocusSession> {
    try {
      const response = await api.post<ApiResponse<HyperfocusSession>>('/api/hyperfocus/sessions', {
        task_id: taskId,
        task_type: taskType
      });
      return response.data.data;
    } catch (error) {
      throw new AppError('Failed to start hyperfocus session', (error as Error).message);
    }
  }

  async endSession(sessionId: string, notes?: string, rating?: number): Promise<HyperfocusSession> {
    try {
      const response = await api.put<ApiResponse<HyperfocusSession>>(`/api/hyperfocus/sessions/${sessionId}/end`, {
        notes,
        rating
      });
      return response.data.data;
    } catch (error) {
      throw new AppError('Failed to end hyperfocus session', (error as Error).message);
    }
  }

  async getActiveSession(): Promise<HyperfocusSession | null> {
    try {
      const response = await api.get<ApiResponse<HyperfocusSession>>('/api/hyperfocus/sessions/active');
      return response.data.data;
    } catch (error) {
      if ((error as { response?: { status: number } })?.response?.status === 404) {
        return null;
      }
      throw new AppError('Failed to fetch active session', (error as Error).message);
    }
  }

  async getSessionStats(): Promise<SessionStats> {
    try {
      const response = await api.get<ApiResponse<SessionStats>>('/api/hyperfocus/statistics');
      return response.data.data;
    } catch (error) {
      throw new AppError('Failed to fetch session stats', (error as Error).message);
    }
  }

  async getSessions(startDate?: Date, endDate?: Date): Promise<HyperfocusSession[]> {
    try {
      const params = new URLSearchParams();
      if (startDate) {
        params.append('start_date', startDate.toISOString());
      }
      if (endDate) {
        params.append('end_date', endDate.toISOString());
      }

      const response = await api.get<ApiResponse<HyperfocusSession[]>>(`/api/hyperfocus/sessions?${params}`);
      return response.data.data;
    } catch (error) {
      throw new AppError('Failed to fetch sessions', (error as Error).message);
    }
  }

  async cancelSession(sessionId: string): Promise<void> {
    try {
      await api.put(`/api/hyperfocus/sessions/${sessionId}/cancel`);
    } catch (error) {
      throw new AppError('Failed to cancel session', (error as Error).message);
    }
  }
} 