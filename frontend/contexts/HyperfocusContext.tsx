// contexts/HyperfocusContext.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';

import { Alert } from 'react-native';

import { API_ENDPOINTS } from '@/core/config';
import { api } from '@/lib/api';

import { useAuth } from './AuthContext';


interface HyperfocusSession {
  id: string;
  user_id: string;
  start_time: string;
  end_time?: string;
  duration_minutes: number;
  status: 'ACTIVE' | 'COMPLETED';
  productivity_score?: number;
  focus_level?: number;
  quality_score?: number;
}

interface HyperfocusStats {
  total_sessions: number;
  total_duration: number;
  average_duration: number;
  average_productivity: number;
  average_focus: number;
  average_quality: number;
  completion_rate: number;
  task_type_distribution: Record<string, number>;
}

interface HyperfocusContextType {
  sessionActive: boolean;
  remainingTime: number;
  currentSession: HyperfocusSession | null;
  stats: HyperfocusStats | null;
  startSession: (duration: number) => Promise<void>;
  endSession: () => Promise<void>;
  logInterruption: (reason: string) => Promise<void>;
}

const HyperfocusContext = createContext<HyperfocusContextType | undefined>(undefined);

// Logging utility
const logHyperfocus = (action: string, data?: any) => {
  const timestamp = new Date().toISOString();
  const logData = {
    timestamp,
    action,
    ...data && { data: typeof data === 'object' ? JSON.stringify(data) : data }
  };
  console.debug('🎯 Hyperfocus:', logData);
};

export const HyperfocusProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [sessionActive, setSessionActive] = useState(false);
  const [remainingTime, setRemainingTime] = useState(0);
  const [currentSession, setCurrentSession] = useState<HyperfocusSession | null>(null);
  const [stats, setStats] = useState<HyperfocusStats | null>(null);
  const { isAuthenticated, isInitialized } = useAuth();

  const handleError = (error: any, defaultMessage: string) => {
    const message = error.response?.data?.detail || defaultMessage;
    console.error('Hyperfocus error:', error);
    Alert.alert('Error', message);
  };

  const startSession = async (duration: number) => {
    if (!isAuthenticated) {
      Alert.alert('Error', 'Please login to start a session');
      return;
    }

    logHyperfocus('start_session_attempt', { duration });
    try {
      const response = await api.post<HyperfocusSession>("/api/hyperfocus/session", {
        duration_minutes: duration,
        purpose: "Focus Session",
        focus_area: "Task Focus"
      });
      logHyperfocus('session_started', { sessionId: response.data.id });
      setCurrentSession(response.data);
      setSessionActive(true);
      setRemainingTime(duration);
    } catch (error) {
      logHyperfocus('start_session_error', { error });
      handleError(error, "Error starting session");
    }
  };

  const endSession = async () => {
    if (!isAuthenticated || !currentSession) return;

    logHyperfocus('end_session_attempt', { sessionId: currentSession.id });
    try {
      await api.post(`/api/hyperfocus/session/${currentSession.id}/end`);
      logHyperfocus('session_ended', { sessionId: currentSession.id });
      setSessionActive(false);
      setRemainingTime(0);
      setCurrentSession(null);
      // Refresh stats after ending session
      fetchStats();
    } catch (error) {
      logHyperfocus('end_session_error', { error });
      handleError(error, "Error ending session");
    }
  };

  const logInterruption = async (reason: string) => {
    if (!isAuthenticated || !currentSession) return;

    logHyperfocus('log_interruption_attempt', { sessionId: currentSession.id, reason });
    try {
      await api.post(`/api/hyperfocus/session/${currentSession.id}/interruption`, { reason });
      logHyperfocus('interruption_logged', { sessionId: currentSession.id });
    } catch (error) {
      logHyperfocus('log_interruption_error', { error });
      handleError(error, "Error logging interruption");
    }
  };

  const fetchStats = async () => {
    if (!isAuthenticated) return;

    logHyperfocus('fetch_stats_attempt');
    try {
      const response = await api.get<HyperfocusStats>("/api/hyperfocus/statistics");
      logHyperfocus('stats_fetched', { stats: response.data });
      setStats(response.data);
    } catch (error) {
      logHyperfocus('fetch_stats_error', { error });
      handleError(error, "Error fetching stats");
    }
  };

  // Only fetch stats when auth is initialized and user is authenticated
  useEffect(() => {
    if (isInitialized && isAuthenticated) {
      fetchStats();
    } else {
      setStats(null);
      setCurrentSession(null);
      setSessionActive(false);
      setRemainingTime(0);
    }
  }, [isInitialized, isAuthenticated]);

  return (
    <HyperfocusContext.Provider
      value={{
        sessionActive,
        remainingTime,
        currentSession,
        stats,
        startSession,
        endSession,
        logInterruption,
      }}
    >
      {children}
    </HyperfocusContext.Provider>
  );
};

export const useHyperfocus = () => {
  const context = useContext(HyperfocusContext);
  if (context === undefined) {
    throw new Error('useHyperfocus must be used within a HyperfocusProvider');
  }
  return context;
};
