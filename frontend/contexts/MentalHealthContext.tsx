import React, { createContext, useContext, useCallback, useMemo } from 'react';

import type { MentalHealthLog} from '@/app/services/mental-health';
import { MentalHealthService } from '@/app/services/mental-health';
import type { CreateMentalHealthLog } from '@/app/types/mental-health';

import { useAuth } from './AuthContext';

export interface MentalHealthStats {
  mood_average: number;
  stress_level_average: number;
  anxiety_level_average: number;
  energy_level_average: number;
  focus_level_average: number;
  sleep_hours_average: number;
  sleep_quality_average: number;
  total_logs: number;
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

export enum MoodLevel {
  VeryLow = 1,
  Low = 2,
  Moderate = 3,
  High = 4,
  VeryHigh = 5
}

export enum StressLevel {
  None = 0,
  Low = 1,
  Moderate = 2,
  High = 3,
  Extreme = 4
}

export enum AnxietyLevel {
  None = 0,
  Low = 1,
  Moderate = 2,
  High = 3,
  Extreme = 4
}

interface MentalHealthContextType {
  stats: MentalHealthStats | null;
  loading: boolean;
  error: string | null;
  createLog: (data: Partial<CreateMentalHealthLog>) => Promise<any>;
  getStats: () => Promise<MentalHealthStats>;
}

const MentalHealthContext = createContext<MentalHealthContextType | undefined>(undefined);

export function MentalHealthProvider({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();
  const [stats, setStats] = React.useState<MentalHealthStats | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const service = useMemo(() => {
    console.debug('Creating mental health service instance:', { userId: user?.id });
    return new MentalHealthService(user?.id || '');
  }, [user?.id]);

  const createLog = useCallback(async (data: Partial<CreateMentalHealthLog>) => {
    console.debug('Starting createLog in MentalHealthContext:', { data, user });
    
    if (!user?.id) {
      console.error('CreateLog failed: User not authenticated');
      throw new Error('User not authenticated');
    }
    
    try {
      console.debug('Transforming log data...');
      // Transform CreateMentalHealthLog to MentalHealthLog
      const logData: MentalHealthLog = {
        userId: user.id,
        mood: String(data.moodScore || 0),
        intensity: data.stressLevel || 0,
        note: data.notes,
        triggers: [],
        timestamp: new Date().toISOString()
      };
      console.debug('Transformed log data:', logData);

      console.debug('Calling service.createLog...');
      const result = await service.createLog(logData);
      console.debug('Service.createLog succeeded:', result);
      return result;
    } catch (error) {
      console.error('CreateLog failed:', error);
      console.error('Error details:', {
        error,
        data,
        user,
        service: !!service
      });
      throw error;
    }
  }, [user?.id, service]);

  const getStats = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await service.getUserStats();
      setStats(result);
      return result;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to get stats';
      setError(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [user?.id, service]);

  const value = {
    stats,
    loading,
    error,
    createLog,
    getStats
  };

  return (
    <MentalHealthContext.Provider value={value}>
      {children}
    </MentalHealthContext.Provider>
  );
}

export function useMentalHealth() {
  const context = useContext(MentalHealthContext);
  if (!context) {
    throw new Error('useMentalHealth must be used within a MentalHealthProvider');
  }
  return context;
} 