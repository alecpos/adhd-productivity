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
  username: string;
  points: number;
  rank: number;
}

interface LeaderboardSchema {
  rankings: LeaderboardEntry[];
  updated_at: string;
}

interface Progress {
  total_points: number;
  level: number;
  next_level_points: number;
  badges_count: number;
  achievements_count: number;
}

interface APIResponse<T> {
  data: T;
  message: string;
}

interface LeaderboardResponse {
  rankings: LeaderboardEntry[];
  updated_at: string;
}

interface Streak {
  current_streak: number;
  longest_streak: number;
  last_activity_date: string;
}

interface GamificationContextType {
  badges: Badge[];
  achievements: Achievement[];
  leaderboard: LeaderboardEntry[];
  progress: Progress | null;
  streak: Streak | null;
  loading: boolean;
  error: string | null;
  fetchGamificationData: () => Promise<void>;
  claimReward: (rewardId: string) => Promise<void>;
  completeChallenge: (challengeId: string) => Promise<void>;
  updateStreak: (activityType: string, date: Date) => Promise<void>;
  getLeaderboard: (type: 'global' | 'friends') => Promise<void>;
  addToLeaderboard: (points: number) => Promise<void>;
}

const GamificationContext = createContext<GamificationContextType>({
  badges: [],
  achievements: [],
  leaderboard: [],
  progress: null,
  streak: null,
  loading: false,
  error: null,
  fetchGamificationData: async () => {},
  claimReward: async () => {},
  completeChallenge: async () => {},
  updateStreak: async () => {},
  getLeaderboard: async () => {},
  addToLeaderboard: async () => {},
});

export const GamificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [badges, setBadges] = useState<Badge[]>([]);
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [progress, setProgress] = useState<Progress | null>(null);
  const [streak, setStreak] = useState<Streak | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();

  const handleError = (err: any, endpoint: string) => {
    console.error(`Error fetching ${endpoint}:`, err);
    // Don't show alerts for 404s as the endpoints might not be implemented yet
    if (err.response?.status !== 404) {
      Alert.alert('Error', err.response?.data?.detail || `Unable to fetch ${endpoint}`);
    }
    return [];
  };

  const fetchGamificationData = async () => {
    if (!user) return;
    setLoading(true);
    try {
      const [badgesRes, achievementsRes, leaderboardRes, progressRes] = await Promise.all([
        api.get<APIResponse<Badge[]>>('/api/gamification/badges'),
        api.get<APIResponse<Achievement[]>>('/api/gamification/achievements'),
        api.get<APIResponse<LeaderboardSchema>>('/api/gamification/leaderboard'),
        api.get<APIResponse<Progress>>('/api/gamification/progress')
      ]);

      setBadges(badgesRes.data.data);
      setAchievements(achievementsRes.data.data);
      setLeaderboard(leaderboardRes.data.data.rankings || []);
      setProgress(progressRes.data.data);
      setError(null);
    } catch (err) {
      handleError(err, 'gamification data');
    } finally {
      setLoading(false);
    }
  };

  const updateStreak = async (activityType: string, date: Date) => {
    if (!user) return;
    try {
      const response = await api.post<APIResponse<Streak>>(`/gamification/streak/${user.id}/update`, {
        activity_type: activityType,
        date: date.toISOString()
      });
      setStreak(response.data.data);
    } catch (err) {
      handleError(err, 'updateStreak');
    }
  };

  const getLeaderboard = async (category?: string, timeframe?: string) => {
    try {
      const params = new URLSearchParams();
      if (category) params.append('category', category);
      if (timeframe) params.append('timeframe', timeframe);

      const response = await api.get<APIResponse<LeaderboardSchema>>(`/api/gamification/leaderboard?${params}`);
      setLeaderboard(response.data.data.rankings || []);
    } catch (err) {
      handleError(err, 'fetching leaderboard');
    }
  };

  const addToLeaderboard = async (points: number) => {
    if (!user) return;
    try {
      const response = await api.post<APIResponse<LeaderboardEntry>>('/gamification/leaderboard/add', {
        user_id: user.id,
        points
      });
      await getLeaderboard('global');
    } catch (err) {
      handleError(err, 'addToLeaderboard');
    }
  };

  const claimReward = async (rewardId: string) => {
    try {
      await api.post(`/api/gamification/claim-reward/${rewardId}`);
      await fetchGamificationData();
    } catch (err) {
      handleError(err, 'claiming reward');
    }
  };

  const completeChallenge = async (challengeId: string) => {
    try {
      await api.post(`/api/gamification/complete-challenge/${challengeId}`);
      await fetchGamificationData();
    } catch (err) {
      handleError(err, 'completing challenge');
    }
  };

  useEffect(() => {
    if (user) {
      fetchGamificationData();
    }
  }, [user]);

  return (
    <GamificationContext.Provider value={{
      badges,
      achievements,
      leaderboard,
      progress,
      streak,
      loading,
      error,
      fetchGamificationData,
      claimReward,
      completeChallenge,
      updateStreak,
      getLeaderboard,
      addToLeaderboard,
    }}>
      {children}
    </GamificationContext.Provider>
  );
};

export const useGamification = () => {
  const context = useContext(GamificationContext);
  if (context === undefined) {
    throw new Error('useGamification must be used within a GamificationProvider');
  }
  return context;
};
