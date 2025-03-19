import React, { createContext, useContext, useState, useCallback } from 'react';

import axios from 'axios';

import { useAuth } from './AuthContext';

interface FocusMetrics {
  focusScore: number;
  interruptions: number;
  totalFocusTime: number;
  averageFocusSpan: number;
}

interface BodyDoublingSession {
  id: string;
  startTime: Date;
  endTime?: Date;
  partner?: string;
  status: 'active' | 'completed' | 'cancelled';
  taskId?: string;
  taskDescription?: string;
  focusMetrics?: FocusMetrics;
  notes?: string;
}

interface SessionStats {
  totalSessions: number;
  averageFocusScore: number;
  totalFocusTime: number;
  preferredPartners: string[];
  mostProductiveTimeSlots: { hour: number; score: number }[];
}

interface BodyDoublingContextType {
  currentSession: BodyDoublingSession | null;
  sessionStats: SessionStats | null;
  loading: boolean;
  error: string | null;
  startSession: (partnerId?: string, taskId?: string, taskDescription?: string) => Promise<void>;
  endSession: (focusScore?: number) => Promise<void>;
  getSessions: (startDate?: Date, endDate?: Date) => Promise<BodyDoublingSession[]>;
  logInterruption: (reason: string) => Promise<void>;
  updateFocusScore: (score: number) => Promise<void>;
  addSessionNote: (note: string) => Promise<void>;
  getSessionStats: () => Promise<void>;
}

const BodyDoublingContext = createContext<BodyDoublingContextType | undefined>(undefined);

export const BodyDoublingProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentSession, setCurrentSession] = useState<BodyDoublingSession | null>(null);
  const [sessionStats, setSessionStats] = useState<SessionStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();

  const handleError = (err: any, operation: string) => {
    console.error(`Error in BodyDoubling ${operation}:`, err);
    setError(err.response?.data?.detail || `Failed to ${operation}`);
    throw err;
  };

  const startSession = useCallback(async (partnerId?: string, taskId?: string, taskDescription?: string) => {
    if (!user) return;
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/body-doubling/start', {
        user_id: user.id,
        partner_id: partnerId,
        task_id: taskId,
        task_description: taskDescription
      });
      setCurrentSession(response.data);
      setError(null);
    } catch (err) {
      handleError(err, 'start session');
    } finally {
      setLoading(false);
    }
  }, [user]);

  const endSession = useCallback(async (focusScore?: number) => {
    if (!currentSession || !user) return;
    setLoading(true);
    try {
      await axios.post(`http://localhost:8000/body-doubling/end/${currentSession.id}`, {
        user_id: user.id,
        focus_score: focusScore
      });
      setCurrentSession(null);
      await getSessionStats();
      setError(null);
    } catch (err) {
      handleError(err, 'end session');
    } finally {
      setLoading(false);
    }
  }, [currentSession, user]);

  const getSessions = useCallback(async (startDate?: Date, endDate?: Date) => {
    if (!user) return [];
    setLoading(true);
    try {
      const response = await axios.get('http://localhost:8000/body-doubling/sessions', {
        params: {
          user_id: user.id,
          start_date: startDate?.toISOString(),
          end_date: endDate?.toISOString()
        }
      });
      setError(null);
      return response.data;
    } catch (err) {
      handleError(err, 'fetch sessions');
      return [];
    } finally {
      setLoading(false);
    }
  }, [user]);

  const logInterruption = useCallback(async (reason: string) => {
    if (!currentSession || !user) return;
    setLoading(true);
    try {
      const response = await axios.post(`http://localhost:8000/body-doubling/interruption/${currentSession.id}`, {
        user_id: user.id,
        reason
      });
      setCurrentSession(prev => prev ? { ...prev, focusMetrics: response.data.focusMetrics } : null);
      setError(null);
    } catch (err) {
      handleError(err, 'log interruption');
    } finally {
      setLoading(false);
    }
  }, [currentSession, user]);

  const updateFocusScore = useCallback(async (score: number) => {
    if (!currentSession || !user) return;
    setLoading(true);
    try {
      const response = await axios.put(`http://localhost:8000/body-doubling/focus/${currentSession.id}`, {
        user_id: user.id,
        focus_score: score
      });
      setCurrentSession(prev => prev ? { ...prev, focusMetrics: response.data.focusMetrics } : null);
      setError(null);
    } catch (err) {
      handleError(err, 'update focus score');
    } finally {
      setLoading(false);
    }
  }, [currentSession, user]);

  const addSessionNote = useCallback(async (note: string) => {
    if (!currentSession || !user) return;
    setLoading(true);
    try {
      const response = await axios.post(`http://localhost:8000/body-doubling/note/${currentSession.id}`, {
        user_id: user.id,
        note
      });
      setCurrentSession(prev => prev ? { ...prev, notes: response.data.notes } : null);
      setError(null);
    } catch (err) {
      handleError(err, 'add note');
    } finally {
      setLoading(false);
    }
  }, [currentSession, user]);

  const getSessionStats = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    try {
      const response = await axios.get(`http://localhost:8000/body-doubling/stats/${user.id}`);
      setSessionStats(response.data);
      setError(null);
    } catch (err) {
      handleError(err, 'fetch stats');
    } finally {
      setLoading(false);
    }
  }, [user]);

  return (
    <BodyDoublingContext.Provider value={{
      currentSession,
      sessionStats,
      loading,
      error,
      startSession,
      endSession,
      getSessions,
      logInterruption,
      updateFocusScore,
      addSessionNote,
      getSessionStats,
    }}>
      {children}
    </BodyDoublingContext.Provider>
  );
};

export const useBodyDoubling = () => {
  const context = useContext(BodyDoublingContext);
  if (context === undefined) {
    throw new Error('useBodyDoubling must be used within a BodyDoublingProvider');
  }
  return context;
}; 