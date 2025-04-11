import { API_ENDPOINTS } from '@/core/config';
import { api } from '@/lib/api';
import { Task, TaskStatus, TaskPriority } from '@/types/task';

export interface CreateTaskRequest {
  user_id: string;
  title: string;
  description?: string;
  due_date?: string;
  priority?: TaskPriority;
  estimated_duration?: number;
  energy_required?: number;
}

export interface TaskStatistics {
  total_tasks: number;
  completed_tasks: number;
  completion_rate: number;
  average_completion_time?: number;
  tasks_by_priority?: Record<TaskPriority, number>;
  tasks_by_status?: Record<TaskStatus, number>;
}

interface APIResponse<T> {
  data: T;
  message?: string;
}

export class TaskService {
  async getTasks(): Promise<Task[]> {
    const response = await api.get<APIResponse<Task[]>>(API_ENDPOINTS.TASKS.BASE);
    return response.data.data;
  }

  async getUserTasks(userId: string): Promise<Task[]> {
    const response = await api.get<APIResponse<Task[]>>(`${API_ENDPOINTS.TASKS.BASE}/user/${userId}`);
    return response.data.data;
  }

  async createTask(task: CreateTaskRequest): Promise<Task> {
    const response = await api.post<APIResponse<Task>>(API_ENDPOINTS.TASKS.BASE, task);
    return response.data.data;
  }

  async updateTask(taskId: string, updates: Partial<Task>): Promise<Task> {
    const response = await api.put<APIResponse<Task>>(`${API_ENDPOINTS.TASKS.BASE}/${taskId}`, updates);
    return response.data.data;
  }

  async deleteTask(taskId: string): Promise<void> {
    await api.delete(`${API_ENDPOINTS.TASKS.BASE}/${taskId}`);
  }

  async completeTask(taskId: string, completionNotes?: string): Promise<Task> {
    const response = await api.post<APIResponse<Task>>(`${API_ENDPOINTS.TASKS.BASE}/${taskId}/complete`, {
      completion_notes: completionNotes
    });
    return response.data.data;
  }

  async getTaskStatistics(): Promise<TaskStatistics> {
    const response = await api.get<APIResponse<TaskStatistics>>(`${API_ENDPOINTS.TASKS.BASE}/statistics`);
    return response.data.data;
  }

  async updateTaskStatus(taskId: string, status: TaskStatus): Promise<Task> {
    return this.updateTask(taskId, { status });
  }

  async updateTaskPriority(taskId: string, priority: TaskPriority): Promise<Task> {
    return this.updateTask(taskId, { priority });
  }
}

export { Task, TaskStatus, TaskPriority };
export const taskService = new TaskService();
