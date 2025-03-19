import { api } from '@/lib/api';

import { AppError } from '../../core/errors';

import type { ApiResponse } from '../../types/common';
import type { Task, TaskStats } from '../../types/task';

export class TaskService {
  private userId: string;

  constructor(userId: string) {
    this.userId = userId;
  }

  async createTask(taskData: Partial<Task>): Promise<ApiResponse<Task>> {
    try {
      const response = await api.post<ApiResponse<Task>>('/tasks', taskData);
      return response.data;
    } catch (error) {
      throw new AppError('Failed to create task', (error as Error).message);
    }
  }

  async updateTask(taskId: string, updates: Partial<Task>): Promise<ApiResponse<Task>> {
    try {
      const response = await api.put<ApiResponse<Task>>(`/tasks/${taskId}`, updates);
      return response.data;
    } catch (error) {
      throw new AppError('Failed to update task', (error as Error).message);
    }
  }

  async deleteTask(taskId: string): Promise<void> {
    try {
      await api.delete(`/api/tasks/${taskId}`);
    } catch (error) {
      throw new AppError('Failed to delete task', (error as Error).message);
    }
  }

  async getTasks(filters?: {
    status?: Task['status'];
    priority?: Task['priority'];
    startDate?: Date;
    endDate?: Date;
    category?: string;
  }): Promise<Task[]> {
    try {
      const params = new URLSearchParams();
      if (filters?.status !== undefined && filters.status !== null) {
        params.append('status', filters.status);
      }
      if (filters?.priority !== undefined && filters.priority !== null) {
        params.append('priority', filters.priority);
      }
      if (filters?.startDate !== undefined && filters.startDate !== null) {
        params.append('start_date', filters.startDate.toISOString());
      }
      if (filters?.endDate !== undefined && filters.endDate !== null) {
        params.append('end_date', filters.endDate.toISOString());
      }
      if (filters?.category !== undefined && filters.category !== null && filters.category !== '') {
        params.append('category', filters.category);
      }

      const response = await api.get<ApiResponse<Task[]>>(`/api/tasks/user/${this.userId}?${params}`);
      return response.data.data;
    } catch (error) {
      throw new AppError('Failed to fetch tasks', (error as Error).message);
    }
  }

  async getTaskStats(): Promise<TaskStats> {
    try {
      const response = await api.get<ApiResponse<TaskStats>>(`/api/tasks/statistics/${this.userId}`);
      return response.data.data;
    } catch (error) {
      throw new AppError('Failed to fetch task stats', (error as Error).message);
    }
  }

  async completeTask(taskId: string, completionData?: {
    actual_duration?: number;
    quality_score?: number;
    difficulty_rating?: number;
  }): Promise<Task> {
    try {
      const response = await api.put<ApiResponse<Task>>(`/api/tasks/${taskId}/complete`, completionData);
      return response.data.data;
    } catch (error) {
      throw new AppError('Failed to complete task', (error as Error).message);
    }
  }
} 