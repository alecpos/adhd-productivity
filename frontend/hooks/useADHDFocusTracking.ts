import { useState, useCallback, useEffect } from 'react';

import { useADHDSettings } from '../contexts/ADHDSettingsContext';

interface FocusSession {
  startTime: Date;
  endTime?: Date;
  taskId?: string;
  focusLevel: number;  // 1-10
  distractions: {
    timestamp: Date;
    type: string;
    duration: number;
    impact: number;
  }[];
  environment: {
    noise: number;  // 1-10
    visualStimuli: number;  // 1-10
    interruptions: number;
    location: string;
  };
  energyLevels: {
    start: number;  // 1-10
    end?: number;
    fluctuations: { timestamp: Date; level: number }[];
  };
}

interface FocusMetrics {
  averageFocusLevel: number;
  longestFocusStreak: number;
  commonDistractions: { type: string; frequency: number }[];
  optimalConditions: {
    timeOfDay: string[];
    environment: {
      noise: number;
      visualStimuli: number;
      location: string[];
    };
    energyLevel: number;
  };
  productiveHours: {
    hour: number;
    productivity: number;
  }[];
}

export const useADHDFocusTracking = () => {
  const { profile, logDistraction } = useADHDSettings();
  const [currentSession, setCurrentSession] = useState<FocusSession | null>(null);
  const [sessions, setSessions] = useState<FocusSession[]>([]);
  const [metrics, setMetrics] = useState<FocusMetrics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const startSession = useCallback((taskId?: string) => {
    const newSession: FocusSession = {
      startTime: new Date(),
      taskId,
      focusLevel: 8,  // Start optimistically
      distractions: [],
      environment: {
        noise: 0,
        visualStimuli: 0,
        interruptions: 0,
        location: 'unspecified',
      },
      energyLevels: {
        start: profile?.energyManagement?.sustainedFocusLimit ? 8 : 5,
        fluctuations: [],
      },
    };
    setCurrentSession(newSession);
    setSessions(prev => [...prev, newSession]);
  }, [profile]);

  const endSession = useCallback(async () => {
    if (!currentSession) return;

    const endTime = new Date();
    const updatedSession: FocusSession = {
      ...currentSession,
      endTime,
      energyLevels: {
        ...currentSession.energyLevels,
        end: calculateEndEnergyLevel(currentSession),
      },
    };

    setSessions(prev => 
      prev.map(s => 
        s.startTime === currentSession.startTime ? updatedSession : s
      )
    );
    setCurrentSession(null);

    // Update metrics after session ends
    await calculateMetrics([...sessions, updatedSession]);
  }, [currentSession, sessions]);

  const recordDistraction = useCallback(async (
    type: string,
    duration: number,
    impact: number
  ) => {
    if (!currentSession) return;

    const distraction = {
      timestamp: new Date(),
      type,
      duration,
      impact,
    };

    const updatedSession = {
      ...currentSession,
      distractions: [...currentSession.distractions, distraction],
      focusLevel: Math.max(1, currentSession.focusLevel - impact),
    };

    setCurrentSession(updatedSession);
    setSessions(prev =>
      prev.map(s =>
        s.startTime === currentSession.startTime ? updatedSession : s
      )
    );

    // Log to ADHD settings
    await logDistraction(type, duration, impact);
  }, [currentSession, logDistraction]);

  const updateEnvironment = useCallback((
    updates: Partial<FocusSession['environment']>
  ) => {
    if (!currentSession) return;

    const updatedSession = {
      ...currentSession,
      environment: {
        ...currentSession.environment,
        ...updates,
      },
    };

    setCurrentSession(updatedSession);
    setSessions(prev =>
      prev.map(s =>
        s.startTime === currentSession.startTime ? updatedSession : s
      )
    );
  }, [currentSession]);

  const recordEnergyFluctuation = useCallback((level: number) => {
    if (!currentSession) return;

    const updatedSession = {
      ...currentSession,
      energyLevels: {
        ...currentSession.energyLevels,
        fluctuations: [
          ...currentSession.energyLevels.fluctuations,
          { timestamp: new Date(), level },
        ],
      },
    };

    setCurrentSession(updatedSession);
    setSessions(prev =>
      prev.map(s =>
        s.startTime === currentSession.startTime ? updatedSession : s
      )
    );
  }, [currentSession]);

  const calculateMetrics = useCallback(async (sessionsData: FocusSession[]) => {
    setLoading(true);
    try {
      const metrics: FocusMetrics = {
        averageFocusLevel: calculateAverageFocus(sessionsData),
        longestFocusStreak: findLongestStreak(sessionsData),
        commonDistractions: analyzeDistractions(sessionsData),
        optimalConditions: findOptimalConditions(sessionsData),
        productiveHours: analyzeProductiveHours(sessionsData),
      };

      setMetrics(metrics);
      return metrics;
    } catch (err: any) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // Load historical sessions and calculate metrics on mount
    // This would typically come from a backend API
    calculateMetrics(sessions).catch(console.error);
  }, []);

  return {
    currentSession,
    sessions,
    metrics,
    loading,
    error,
    startSession,
    endSession,
    recordDistraction,
    updateEnvironment,
    recordEnergyFluctuation,
  };
};

// Helper functions
const calculateEndEnergyLevel = (session: FocusSession): number => {
  const lastFluctuation = session.energyLevels.fluctuations.slice(-1)[0];
  if (lastFluctuation) return lastFluctuation.level;
  
  // If no fluctuations recorded, estimate based on duration and distractions
  const duration = session.endTime 
    ? (session.endTime.getTime() - session.startTime.getTime()) / (1000 * 60)
    : 0;
  const distractionImpact = session.distractions.reduce((sum, d) => sum + d.impact, 0);
  
  return Math.max(1, Math.min(10,
    session.energyLevels.start - (duration / 30) - (distractionImpact / 2)
  ));
};

const calculateAverageFocus = (sessions: FocusSession[]): number => {
  if (sessions.length === 0) return 0;
  const sum = sessions.reduce((acc, session) => acc + session.focusLevel, 0);
  return sum / sessions.length;
};

const findLongestStreak = (sessions: FocusSession[]): number => {
  return sessions.reduce((max, session) => {
    const duration = session.endTime
      ? (session.endTime.getTime() - session.startTime.getTime()) / (1000 * 60)
      : 0;
    return Math.max(max, duration);
  }, 0);
};

const analyzeDistractions = (sessions: FocusSession[]): { type: string; frequency: number }[] => {
  const distractionCounts = new Map<string, number>();
  
  sessions.forEach(session => {
    session.distractions.forEach(distraction => {
      const count = distractionCounts.get(distraction.type) || 0;
      distractionCounts.set(distraction.type, count + 1);
    });
  });

  return Array.from(distractionCounts.entries())
    .map(([type, frequency]) => ({ type, frequency }))
    .sort((a, b) => b.frequency - a.frequency);
};

const findOptimalConditions = (sessions: FocusSession[]) => {
  const highFocusSessions = sessions.filter(s => s.focusLevel >= 7);
  
  if (highFocusSessions.length === 0) {
    return {
      timeOfDay: [],
      environment: {
        noise: 5,
        visualStimuli: 5,
        location: [],
      },
      energyLevel: 5,
    };
  }

  const timeOfDay = findOptimalTimeRanges(highFocusSessions);
  const locations = findCommonLocations(highFocusSessions);
  const avgNoise = average(highFocusSessions.map(s => s.environment.noise));
  const avgVisualStimuli = average(highFocusSessions.map(s => s.environment.visualStimuli));
  const avgEnergyLevel = average(highFocusSessions.map(s => s.energyLevels.start));

  return {
    timeOfDay,
    environment: {
      noise: avgNoise,
      visualStimuli: avgVisualStimuli,
      location: locations,
    },
    energyLevel: avgEnergyLevel,
  };
};

const analyzeProductiveHours = (sessions: FocusSession[]): { hour: number; productivity: number }[] => {
  const hourlyScores = new Map<number, { total: number; count: number }>();

  sessions.forEach(session => {
    const hour = session.startTime.getHours();
    const current = hourlyScores.get(hour) || { total: 0, count: 0 };
    hourlyScores.set(hour, {
      total: current.total + session.focusLevel,
      count: current.count + 1,
    });
  });

  return Array.from(hourlyScores.entries())
    .map(([hour, { total, count }]) => ({
      hour,
      productivity: total / count,
    }))
    .sort((a, b) => b.productivity - a.productivity);
};

// Utility functions
const findOptimalTimeRanges = (sessions: FocusSession[]): string[] => {
  // Group sessions by hour and find hours with consistently high focus
  const hourlyFocus = new Map<number, number[]>();
  
  sessions.forEach(session => {
    const hour = session.startTime.getHours();
    const focusLevels = hourlyFocus.get(hour) || [];
    hourlyFocus.set(hour, [...focusLevels, session.focusLevel]);
  });

  return Array.from(hourlyFocus.entries())
    .filter(([_, levels]) => average(levels) >= 7)
    .map(([hour, _]) => `${hour}:00`)
    .sort();
};

const findCommonLocations = (sessions: FocusSession[]): string[] => {
  const locationCounts = new Map<string, number>();
  
  sessions.forEach(session => {
    const count = locationCounts.get(session.environment.location) || 0;
    locationCounts.set(session.environment.location, count + 1);
  });

  return Array.from(locationCounts.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3)
    .map(([location, _]) => location);
};

const average = (numbers: number[]): number => {
  if (numbers.length === 0) return 0;
  return numbers.reduce((sum, n) => sum + n, 0) / numbers.length;
}; 