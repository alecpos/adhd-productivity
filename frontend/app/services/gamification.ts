import { AppError } from '@/core/errors';
import { api } from '@/lib/api';
import type { ApiResponse } from '@/types/common';

export interface Badge {
  id: string;
  name: string;
  description: string;
  imageUrl?: string;
  unlockedAt?: string;
  category: string;
  requirements: {
    type: string;
    value: number;
  };
}

export interface Achievement {
  id: string;
  name: string;
  description: string;
  progress: number;
  completed: boolean;
  completedAt?: string;
  requirements: {
    type: string;
    target: number;
  };
}

export interface Streak {
  type: string;
  current: number;
  longest: number;
  lastUpdated: string;
  milestones: {
    target: number;
    reached: boolean;
    reachedAt?: string;
  }[];
}

export interface GamificationProgress {
  points: number;
  level: number;
  badges: Badge[];
  achievements: Achievement[];
  streaks: Streak[];
}

export class GamificationService {
  private userId: string;

  constructor(userId: string) {
    this.userId = userId;
  }

  async getUserProgress(): Promise<GamificationProgress> {
    try {
      const response = await api.get<ApiResponse<GamificationProgress>>(`/api/gamification/user/${this.userId}/progress`);
      return response.data.data;
    } catch (error) {
      throw new AppError('Failed to fetch gamification progress', error instanceof Error ? error.message : 'Unknown error');
    }
  }

  // ... rest of existing code ...
} 