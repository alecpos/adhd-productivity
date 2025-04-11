import type { TimeBlock, SchedulingSuggestion, SchedulingDecision } from '@/app/types/block-schedule';
import { api } from '@/lib/api';

export interface SchedulingRequest {
  taskName: string;
  requiredHours: number;
  deadline?: Date;
  preferredTimeOfDay?: 'morning' | 'afternoon' | 'evening';
  priority?: number;
}

class SchedulingService {
  async checkAvailability(request: SchedulingRequest): Promise<SchedulingSuggestion> {
    try {
      const response = await api.post<SchedulingSuggestion>('/api/scheduling/check-availability', request);
      return response.data;
    } catch (error) {
      console.error('Error checking availability:', error);
      throw error;
    }
  }

  async scheduleTask(blocks: TimeBlock[]): Promise<void> {
    try {
      await api.post('/api/scheduling/schedule-blocks', { blocks });
    } catch (error) {
      console.error('Error scheduling task:', error);
      throw error;
    }
  }

  async createSchedule(userId: string): Promise<void> {
    try {
      await api.post('/api/scheduling/create', { userId });
    } catch (error) {
      console.error('Error creating schedule:', error);
      throw error;
    }
  }

  async getSuggestions(id: string): Promise<SchedulingSuggestion> {
    try {
      const response = await api.get<SchedulingSuggestion>(`/api/scheduling/suggestions/${id}`);
      return response.data;
    } catch (error) {
      console.error('Error getting suggestions:', error);
      throw error;
    }
  }

  async getDecisionDetails(decisionId: string): Promise<SchedulingDecision> {
    try {
      const response = await api.get<SchedulingDecision>(`/api/scheduling/decisions/${decisionId}`);
      return response.data;
    } catch (error) {
      console.error('Error getting decision details:', error);
      throw error;
    }
  }
}

export const schedulingService = new SchedulingService();
export default SchedulingService;
