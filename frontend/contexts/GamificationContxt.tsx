import React, { createContext, useState, useContext, useEffect } from 'react';

import { Alert } from 'react-native';

import { api } from '@/lib/api';

import { useAuth } from './AuthContext';

interface Badge {
  id: string;
  name: string;
  description: string;
  category: string;
  level: number;
  earned_at: string;
  meta_data: {
    icon_url: string;
  };
}

interface Achievement {
  id: string;
  name: string;
  description: string;
  category: string;
  points: number;
  earned_at: string;
  meta_data: {
    progress: number;
    completed: boolean;
  };
}

interface LeaderboardEntry {
  user_id: string;
  score: number;
  rank: number;
}

interface Streak {
  user_id: string;
  current_streak: number;
  longest_streak: number;
  streak_type: string;
  last_activity: string;
}

interface Points {
  total_points: number;
  level: number;
}

interface DashboardData {
  streaks: Streak | null;
  leaderboard: {
    entries: LeaderboardEntry[];
  };
  points: Points;
  badges: Badge[];
  achievements: Achievement[];
}

interface GamificationContextType {
  dashboard: DashboardData | null;
  loading: boolean;
  error: string | null;
  fetchGamificationData: () => Promise<void>;
}

const defaultDashboard: DashboardData = {
  streaks: null,
  leaderboard: { entries: [] },
  points: { total_points: 0, level: 1 },
  badges: [],
  achievements: []
};

const GamificationContext = createContext<GamificationContextType>({
  dashboard: defaultDashboard,
  loading: true,
  error: null,
  fetchGamificationData: async () => {},
});

export const GamificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [dashboard, setDashboard] = useState<DashboardData | null>(defaultDashboard);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();

  const fetchGamificationData = async () => {
    if (!user) {
      setError('User not authenticated.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await api.get<{ data: DashboardData }>('/api/gamification/user-dashboard');
      setDashboard(response.data.data);
    } catch (error: any) {
      console.error('Error fetching gamification data:', error);
      setError(error.response?.data?.detail || 'Failed to fetch gamification data');
      setDashboard(defaultDashboard);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) {
      fetchGamificationData();
    } else {
      setDashboard(defaultDashboard);
    }
  }, [user]);

  return (
    <GamificationContext.Provider
      value={{
        dashboard,
        loading,
        error,
        fetchGamificationData,
      }}
    >
      {children}
    </GamificationContext.Provider>
  );
};

export const useGamification = () => {
  const context = useContext(GamificationContext);
  if (!context) {
    throw new Error('useGamification must be used within a GamificationProvider');
  }
  return context;
};
