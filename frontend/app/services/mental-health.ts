import { AppError } from '@/core/errors';
import { api } from '@/lib/api';
import type { ApiResponse } from '@/types/common';

export interface MentalHealthLog {
  userId: string;
  mood: string;
  intensity: number;
  note?: string;
  triggers?: string[];
  timestamp: string;
}

export interface MentalHealthStats {
  total_logs: number;
  mood_average: number;
  stress_level_average: number;
  anxiety_level_average: number;
  energy_level_average: number;
  focus_level_average: number;
  sleep_hours_average: number;
  sleep_quality_average: number;
  recent_moods: Array<{
    date: string;
    mood: number;
    notes?: string;
  }>;
  streak: number;
  most_common_activities: string[];
  most_common_triggers: string[];
  most_common_coping_strategies: string[];
  updated_at: string;
}

export class MentalHealthService {
  private _userId: string;

  constructor(userId: string) {
    this._userId = userId;
  }

  get userId(): string {
    return this._userId;
  }

  async getUserStats(): Promise<MentalHealthStats> {
    try {
      const response = await api.get<ApiResponse<MentalHealthStats>>(`/api/mental-health/stats/${this._userId}`);
      return response.data.data;
    } catch (error) {
      console.error('Error fetching mental health stats:', error);
      throw new AppError('Failed to fetch mental health stats', error instanceof Error ? error.message : 'Unknown error');
    }
  }

  async createLog(data: MentalHealthLog): Promise<ApiResponse<MentalHealthLog>> {
    try {
      const response = await api.post<ApiResponse<MentalHealthLog>>('/api/mental-health/logs', data);
      return response.data;
    } catch (error) {
      throw new AppError('Failed to create mental health log', error instanceof Error ? error.message : 'Unknown error');
    }
  }

  async getLogs(userId: string, startDate?: Date, endDate?: Date): Promise<ApiResponse<MentalHealthLog[]>> {
    try {
      const params = {
        userId,
        ...(startDate && { startDate: startDate.toISOString() }),
        ...(endDate && { endDate: endDate.toISOString() }),
      };
      const response = await api.get<ApiResponse<MentalHealthLog[]>>('/api/mental-health/logs', { params });
      return response.data;
    } catch (error) {
      throw new AppError('Failed to fetch mental health logs', error instanceof Error ? error.message : 'Unknown error');
    }
  }

  async analyzeMood(userId: string, period: 'day' | 'week' | 'month' = 'week'): Promise<ApiResponse<MentalHealthStats>> {
    try {
      const response = await api.get<ApiResponse<MentalHealthStats>>(`/mental-health/analyze/${userId}`, {
        params: { period }
      });
      return response.data;
    } catch (error) {
      throw new AppError('Failed to analyze mood', error instanceof Error ? error.message : 'Unknown error');
    }
  }

  async getStats(): Promise<MentalHealthStats> {
    return this.getUserStats();
  }
}

// Create a singleton instance
let mentalHealthService: MentalHealthService | null = null;

export function getMentalHealthService(userId: string): MentalHealthService {
  if (!mentalHealthService || mentalHealthService.userId !== userId) {
    mentalHealthService = new MentalHealthService(userId);
  }
  return mentalHealthService;
}

export default getMentalHealthService;
