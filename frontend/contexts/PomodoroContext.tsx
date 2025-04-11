import React, { createContext, useContext, useState, useCallback } from 'react';

import { PomodoroService } from '../core/api/services/pomodoroService';

import { useAuth } from './AuthContext';

import type { PomodoroSession, PomodoroSessionStats, StartSessionRequest } from '../core/api/services/pomodoroService';



interface PomodoroContextType {
  sessions: PomodoroSession[];
  currentSession: PomodoroSession | null;
  loading: boolean;
  error: string | null;
  stats: PomodoroSessionStats | null;
  fetchSessions: () => Promise<void>;
  startSession: (sessionData: Omit<StartSessionRequest, "user_id">) => Promise<PomodoroSession>;
  endSession: (sessionId: string) => Promise<PomodoroSession>;
  pauseSession: (sessionId: string) => Promise<PomodoroSession>;
  resumeSession: (sessionId: string) => Promise<PomodoroSession>;
  getSessionStats: () => Promise<void>;
  updateSession: (sessionId: string, data: Partial<PomodoroSession>) => Promise<PomodoroSession>;
}

const PomodoroContext = createContext<PomodoroContextType | undefined>(undefined);

export function usePomodoro() {
  const context = useContext(PomodoroContext);
  if (!context) {
    throw new Error('usePomodoro must be used within a PomodoroProvider');
  }
  return context;
}

export function PomodoroProvider({ children }: { children: React.ReactNode }) {
  const [sessions, setSessions] = useState<PomodoroSession[]>([]);
  const [currentSession, setCurrentSession] = useState<PomodoroSession | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<PomodoroSessionStats | null>(null);
  const { user } = useAuth();

  const fetchSessions = useCallback(async () => {
    if (!user?.id) return;

    setLoading(true);
    setError(null);
    try {
      const fetchedSessions = await PomodoroService.getUserSessions();
      setSessions(fetchedSessions);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch sessions');
      console.error('Error fetching sessions:', err);
    } finally {
      setLoading(false);
    }
  }, [user?.id]);

  const startSession = async (sessionData: Omit<StartSessionRequest, "user_id">) => {
    if (!user?.id) {
      throw new Error('User not authenticated');
    }

    setError(null);
    try {
      const newSession = await PomodoroService.startSession(sessionData);
      setSessions(prev => [...prev, newSession]);
      setCurrentSession(newSession);
      return newSession;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start session');
      throw err;
    }
  };

  const endSession = async (sessionId: string) => {
    setError(null);
    try {
      const updatedSession = await PomodoroService.endSession(sessionId);
      setSessions(prev => prev.map(session =>
        session.id === sessionId ? updatedSession : session
      ));
      setCurrentSession(null);
      await getSessionStats(); // Refresh stats after ending session
      return updatedSession;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to end session');
      throw err;
    }
  };

  const pauseSession = async (sessionId: string) => {
    setError(null);
    try {
      const updatedSession = await PomodoroService.pauseSession(sessionId);
      setSessions(prev => prev.map(session =>
        session.id === sessionId ? updatedSession : session
      ));
      if (currentSession?.id === sessionId) {
        setCurrentSession(updatedSession);
      }
      return updatedSession;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to pause session');
      throw err;
    }
  };

  const resumeSession = async (sessionId: string) => {
    setError(null);
    try {
      const updatedSession = await PomodoroService.resumeSession(sessionId);
      setSessions(prev => prev.map(session =>
        session.id === sessionId ? updatedSession : session
      ));
      if (currentSession?.id === sessionId) {
        setCurrentSession(updatedSession);
      }
      return updatedSession;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to resume session');
      throw err;
    }
  };

  const getSessionStats = async () => {
    if (!user?.id) return;

    try {
      const sessionStats = await PomodoroService.getSessionStats();
      setStats(sessionStats);
    } catch (err) {
      console.error('Error fetching session stats:', err);
    }
  };

  const updateSession = async (sessionId: string, data: Partial<PomodoroSession>) => {
    setError(null);
    try {
      const updatedSession = await PomodoroService.updateSession(sessionId, data);
      setSessions(prev => prev.map(session =>
        session.id === sessionId ? updatedSession : session
      ));
      if (currentSession?.id === sessionId) {
        setCurrentSession(updatedSession);
      }
      return updatedSession;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update session');
      throw err;
    }
  };

  // Fetch sessions and stats when the user changes
  React.useEffect(() => {
    if (user?.id) {
      fetchSessions();
      getSessionStats();
    }
  }, [user?.id, fetchSessions]);

  return (
    <PomodoroContext.Provider
      value={{
        sessions,
        currentSession,
        loading,
        error,
        stats,
        fetchSessions,
        startSession,
        endSession,
        pauseSession,
        resumeSession,
        getSessionStats,
        updateSession,
      }}
    >
      {children}
    </PomodoroContext.Provider>
  );
}
