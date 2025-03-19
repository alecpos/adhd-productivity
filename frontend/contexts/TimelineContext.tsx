import React, { createContext, useContext, useState, useCallback } from 'react';

import axios from 'axios';

import { useAuth } from './AuthContext';

import type { AxiosError } from 'axios';


interface TimeRange {
  start: string; // HH:mm format
  end: string;   // HH:mm format
}

interface EnergyPattern {
  lowEnergyPeriods: TimeRange[];
  highEnergyPeriods: TimeRange[];
  defaultEnergyLevel: 'high' | 'medium' | 'low';
}

interface FocusMetrics {
  focusScore: number;
  interruptions: number;
  totalFocusTime: number;
  averageFocusSpan: number;
}

interface TaskDependency {
  taskId: string;
  type: 'blocks' | 'requires' | 'suggests';
  condition?: {
    type: 'completion' | 'start' | 'energy_level' | 'focus_level';
    value: string | number | boolean;
  };
}

interface TaskSequence {
  id: string;
  tasks: string[];
  type: 'fixed' | 'flexible';
  energyProfile: {
    startLevel: number;
    peakLevel: number;
    endLevel: number;
  };
  breakStrategy: {
    frequency: number;
    duration: number;
  };
}

interface ConflictInfo {
  type: 'energy' | 'focus' | 'time' | 'dependency';
  severity: 'high' | 'medium' | 'low';
  description: string;
  affectedEvents: string[];
  suggestedResolutions: {
    type: 'reschedule' | 'split' | 'adjust_energy' | 'adjust_focus';
    impact: number;
    details: Record<string, unknown>;
  }[];
}

interface TimelineEvent {
  id: string;
  type: 'task' | 'break' | 'hyperfocus' | 'pomodoro' | 'body_doubling';
  startTime: Date;
  endTime?: Date;
  title: string;
  description?: string;
  status: 'planned' | 'in_progress' | 'completed' | 'cancelled';
  energyRequired?: number;
  focusRequired?: number;
  actualEnergyLevel?: number;
  actualFocusLevel?: number;
  focusMetrics?: FocusMetrics;
  metadata?: {
    tags: string[];
    category?: string;
    priority?: number;
    difficulty?: number;
    recurring?: boolean;
    recurrencePattern?: string;
  };
  dependencies?: TaskDependency[];
  sequenceId?: string;
  sequencePosition?: number;
  conflicts?: ConflictInfo[];
  energyProfile?: {
    predicted: number;
    actual: number;
    variance: number;
    factors: string[];
  };
  focusProfile?: {
    predicted: number;
    actual: number;
    variance: number;
    distractions: { time: Date; type: string; duration: number }[];
  };
}

interface TimelineStats {
  mostProductiveHours: { hour: number; productivity: number }[];
  averageEnergyLevels: { hour: number; energy: number }[];
  averageFocusLevels: { hour: number; focus: number }[];
  completionRates: {
    daily: number;
    weekly: number;
    monthly: number;
  };
  dependencyMetrics: {
    completionRate: number;
    averageChainLength: number;
    bottlenecks: string[];
  };
  sequenceMetrics: {
    completionRate: number;
    optimalOrderingRate: number;
    breakAdherence: number;
  };
  conflictMetrics: {
    byType: { [key: string]: number };
    resolutionRate: number;
    commonPatterns: string[];
  };
}

interface Resolution {
  type: 'reschedule' | 'split' | 'adjust_energy' | 'adjust_focus';
  impact: number;
  details: Record<string, unknown>;
}

interface ErrorResponse {
  detail?: string;
  message?: string;
}

interface TaskPrediction {
  prediction: number;
}

interface EventChainResponse {
  upstream: string[];
  downstream: string[];
}

interface ImpactAnalysisResponse {
  affectedEvents: string[];
  severity: 'high' | 'medium' | 'low';
  recommendations: string[];
}

interface DependencyValidation {
  valid: boolean;
  issues: string[];
}

interface TaskDependencyResponse {
  dependencies: TaskDependency[];
}

interface TaskSequenceResponse {
  sequence: TaskSequence;
}

interface ConflictResponse {
  conflicts: ConflictInfo[];
}

interface FocusMetricsResponse {
  focusMetrics: FocusMetrics;
}

interface TimelineContextType {
  events: TimelineEvent[];
  stats: TimelineStats | null;
  energyPattern: EnergyPattern | null;
  loading: boolean;
  error: string | null;
  fetchEvents: (startDate: Date, endDate: Date) => Promise<void>;
  addEvent: (event: Omit<TimelineEvent, 'id'>) => Promise<void>;
  updateEvent: (id: string, updates: Partial<TimelineEvent>) => Promise<void>;
  deleteEvent: (id: string) => Promise<void>;
  updateEnergyPattern: (pattern: EnergyPattern) => Promise<void>;
  getTimelineStats: (startDate: Date, endDate: Date) => Promise<void>;
  logFocusMetrics: (eventId: string, metrics: Partial<FocusMetrics>) => Promise<void>;
  getEnergyForecast: (date: Date) => Promise<{ hour: number; prediction: 'high' | 'medium' | 'low' }[]>;
  sequences: TaskSequence[];
  conflicts: ConflictInfo[];
  createSequence: (sequence: Omit<TaskSequence, 'id'>) => Promise<void>;
  updateSequence: (id: string, updates: Partial<TaskSequence>) => Promise<void>;
  deleteSequence: (id: string) => Promise<void>;
  addDependency: (taskId: string, dependency: TaskDependency) => Promise<void>;
  removeDependency: (taskId: string, dependencyTaskId: string) => Promise<void>;
  validateDependencies: (taskId: string) => Promise<DependencyValidation>;
  detectConflicts: (startDate: Date, endDate: Date) => Promise<ConflictInfo[]>;
  resolveConflict: (eventId: string, resolution: Resolution) => Promise<void>;
  optimizeSequence: (sequenceId: string) => Promise<void>;
  reorderSequence: (sequenceId: string, newOrder: string[]) => Promise<void>;
  predictEnergyLevel: (eventId: string) => Promise<number>;
  predictFocusLevel: (eventId: string) => Promise<number>;
  getEventChain: (eventId: string) => Promise<EventChainResponse>;
  analyzeImpact: (eventId: string, change: Partial<TimelineEvent>) => Promise<ImpactAnalysisResponse>;
}

const TimelineContext = createContext<TimelineContextType | undefined>(undefined);

export const TimelineProvider: React.FC<{ children: React.ReactNode }> = ({ children }): JSX.Element => {
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [stats, setStats] = useState<TimelineStats | null>(null);
  const [energyPattern, setEnergyPattern] = useState<EnergyPattern | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();
  const [sequences, setSequences] = useState<TaskSequence[]>([]);

  const handleError = (err: AxiosError<ErrorResponse> | Error, operation: string): never => {
    const axiosError = err as AxiosError<ErrorResponse>;
    const errorMessage = axiosError.response?.data?.detail ?? axiosError.message ?? `Failed to ${operation}`;
    setError(errorMessage);
    throw err;
  };

  const fetchEvents = useCallback(async (startDate: Date, endDate: Date): Promise<void> => {
    if (!user?.id) return;
    setLoading(true);
    try {
      const response = await axios.get<TimelineEvent[]>('http://localhost:8000/timeline/events', {
        params: {
          user_id: user.id,
          start_date: startDate.toISOString(),
          end_date: endDate.toISOString()
        }
      });
      setEvents(response.data);
      setError(null);
    } catch (err) {
      handleError(err as AxiosError<ErrorResponse>, 'fetch events');
    } finally {
      setLoading(false);
    }
  }, [user]);

  const addEvent = useCallback(async (event: Omit<TimelineEvent, 'id'>): Promise<void> => {
    if (!user?.id) return;
    setLoading(true);
    try {
      const response = await axios.post<TimelineEvent>('http://localhost:8000/timeline/events', {
        ...event,
        user_id: user.id
      });
      setEvents(prev => [...prev, response.data]);
      setError(null);
    } catch (err) {
      handleError(err as AxiosError<ErrorResponse>, 'add event');
    } finally {
      setLoading(false);
    }
  }, [user]);

  const updateEvent = useCallback(async (id: string, updates: Partial<TimelineEvent>): Promise<void> => {
    if (!user?.id) return;
    setLoading(true);
    try {
      const response = await axios.put<TimelineEvent>(`http://localhost:8000/timeline/events/${id}`, {
        ...updates,
        user_id: user.id
      });
      setEvents(prev => prev.map(event => event.id === id ? response.data : event));
      setError(null);
    } catch (err) {
      handleError(err as AxiosError<ErrorResponse>, 'update event');
    } finally {
      setLoading(false);
    }
  }, [user]);

  const deleteEvent = useCallback(async (id: string): Promise<void> => {
    if (!user?.id) return;
    setLoading(true);
    try {
      await axios.delete(`http://localhost:8000/timeline/events/${id}`, {
        params: { user_id: user.id }
      });
      setEvents(prev => prev.filter(event => event.id !== id));
      setError(null);
    } catch (err) {
      handleError(err as AxiosError<ErrorResponse>, 'delete event');
    } finally {
      setLoading(false);
    }
  }, [user]);

  const updateEnergyPattern = useCallback(async (pattern: EnergyPattern) => {
    if (!user) return;
    setLoading(true);
    try {
      const response = await axios.put(`http://localhost:8000/timeline/energy-pattern/${user.id}`, pattern);
      setEnergyPattern(response.data);
      setError(null);
    } catch (err) {
      handleError(err as AxiosError<ErrorResponse>, 'update energy pattern');
    } finally {
      setLoading(false);
    }
  }, [user]);

  const getTimelineStats = useCallback(async (startDate: Date, endDate: Date): Promise<void> => {
    if (!user?.id) return;
    setLoading(true);
    try {
      const response = await axios.get<TimelineStats>('http://localhost:8000/timeline/stats', {
        params: {
          user_id: user.id,
          start_date: startDate.toISOString(),
          end_date: endDate.toISOString()
        }
      });
      setStats(response.data);
      setError(null);
    } catch (err) {
      handleError(err as AxiosError<ErrorResponse>, 'fetch stats');
    } finally {
      setLoading(false);
    }
  }, [user]);

  const logFocusMetrics = useCallback(async (eventId: string, metrics: Partial<FocusMetrics>): Promise<void> => {
    if (!user?.id) return;
    setLoading(true);
    try {
      const response = await axios.post<FocusMetricsResponse>(`http://localhost:8000/timeline/events/${eventId}/focus`, {
        user_id: user.id,
        ...metrics
      });
      setEvents(prev => prev.map(event => 
        event.id === eventId ? { ...event, focusMetrics: response.data.focusMetrics } : event
      ));
      setError(null);
    } catch (err) {
      handleError(err as AxiosError<ErrorResponse>, 'log focus metrics');
    } finally {
      setLoading(false);
    }
  }, [user]);

  const getEnergyForecast = useCallback(async (date: Date): Promise<{ hour: number; prediction: 'high' | 'medium' | 'low' }[]> => {
    if (!user?.id) return [];
    try {
      const response = await axios.get<{ hour: number; prediction: 'high' | 'medium' | 'low' }[]>(
        'http://localhost:8000/timeline/energy-forecast',
        {
          params: {
            user_id: user.id,
            date: date.toISOString()
          }
        }
      );
      return response.data;
    } catch (err) {
      handleError(err as AxiosError<ErrorResponse>, 'get energy forecast');
      return [];
    }
  }, [user]);

  const createSequence = useCallback(async (sequence: Omit<TaskSequence, 'id'>): Promise<void> => {
    if (!user?.id) return;
    setLoading(true);
    try {
      const response = await axios.post<TaskSequenceResponse>(`http://localhost:8000/timeline/sequences`, {
        ...sequence,
        user_id: user.id
      });
      setSequences(prev => [...prev, response.data.sequence]);
      setError(null);
    } catch (err) {
      handleError(err as AxiosError<ErrorResponse>, 'create sequence');
    } finally {
      setLoading(false);
    }
  }, [user]);

  const updateSequence = useCallback(async (id: string, updates: Partial<TaskSequence>): Promise<void> => {
    if (!user?.id) return;
    setLoading(true);
    try {
      const response = await axios.put<TaskSequenceResponse>(`http://localhost:8000/timeline/sequences/${id}`, {
        user_id: user.id,
        ...updates
      });
      setSequences(prev => prev.map(seq => 
        seq.id === id ? response.data.sequence : seq
      ));
      setError(null);
    } catch (err) {
      handleError(err as AxiosError<ErrorResponse>, 'update sequence');
    } finally {
      setLoading(false);
    }
  }, [user]);

  const deleteSequence = useCallback(async (id: string) => {
    if (!user) return;
    setLoading(true);
    try {
      await axios.delete(`http://localhost:8000/timeline/sequences/${id}`, {
        params: { user_id: user.id }
      });
      setSequences(prev => prev.filter(seq => seq.id !== id));
      setError(null);
    } catch (err) {
      handleError(err as AxiosError<ErrorResponse>, 'delete sequence');
    } finally {
      setLoading(false);
    }
  }, [user]);

  const addDependency = useCallback(async (taskId: string, dependency: TaskDependency): Promise<void> => {
    if (!user?.id) return;
    setLoading(true);
    try {
      const response = await axios.post<TaskDependencyResponse>(`http://localhost:8000/timeline/tasks/${taskId}/dependencies`, {
        user_id: user.id,
        dependency
      });
      setEvents(prev => prev.map(event => 
        event.id === taskId 
          ? { ...event, dependencies: response.data.dependencies }
          : event
      ));
      setError(null);
    } catch (err) {
      handleError(err as AxiosError<ErrorResponse>, 'add dependency');
    } finally {
      setLoading(false);
    }
  }, [user]);

  const removeDependency = useCallback(async (taskId: string, dependencyTaskId: string) => {
    if (!user) return;
    setLoading(true);
    try {
      await axios.delete(`http://localhost:8000/timeline/events/${taskId}/dependencies/${dependencyTaskId}`, {
        params: { user_id: user.id }
      });
      setEvents(prev => prev.map(event => 
        event.id === taskId ? {
          ...event,
          dependencies: event.dependencies?.filter(d => d.taskId !== dependencyTaskId)
        } : event
      ));
      setError(null);
    } catch (err) {
      handleError(err as AxiosError<ErrorResponse>, 'remove dependency');
    } finally {
      setLoading(false);
    }
  }, [user]);

  const validateDependencies = useCallback(async (taskId: string): Promise<DependencyValidation> => {
    if (!user?.id) return { valid: false, issues: ['User not authenticated'] };
    try {
      const response = await axios.get<DependencyValidation>(`http://localhost:8000/timeline/tasks/${taskId}/validate-dependencies`, {
        params: { user_id: user.id }
      });
      return response.data;
    } catch (err) {
      handleError(err as AxiosError<ErrorResponse>, 'validate dependencies');
      return { valid: false, issues: ['Validation failed'] };
    }
  }, [user]);

  const detectConflicts = useCallback(async (startDate: Date, endDate: Date): Promise<ConflictInfo[]> => {
    if (!user?.id) return [];
    try {
      const response = await axios.get<ConflictResponse>('http://localhost:8000/timeline/conflicts', {
        params: {
          user_id: user.id,
          start_date: startDate.toISOString(),
          end_date: endDate.toISOString()
        }
      });
      return response.data.conflicts;
    } catch (err) {
      handleError(err as AxiosError<ErrorResponse>, 'detect conflicts');
      return [];
    }
  }, [user]);

  const resolveConflict = useCallback(async (eventId: string, resolution: Resolution): Promise<void> => {
    if (!user?.id) return;
    setLoading(true);
    try {
      await axios.post<void>(`http://localhost:8000/timeline/events/${eventId}/resolve-conflict`, {
        resolution,
        user_id: user.id
      });
      setError(null);
    } catch (err) {
      handleError(err as AxiosError<ErrorResponse>, 'resolve conflict');
    } finally {
      setLoading(false);
    }
  }, [user]);

  const optimizeSequence = useCallback(async (sequenceId: string): Promise<void> => {
    if (!user?.id) return;
    setLoading(true);
    try {
      const response = await axios.post<TaskSequenceResponse>(`http://localhost:8000/timeline/sequences/${sequenceId}/optimize`, {
        user_id: user.id
      });
      setSequences(prev => prev.map(seq => 
        seq.id === sequenceId ? response.data.sequence : seq
      ));
      setError(null);
    } catch (err) {
      handleError(err as AxiosError<ErrorResponse>, 'optimize sequence');
    } finally {
      setLoading(false);
    }
  }, [user]);

  const reorderSequence = useCallback(async (sequenceId: string, newOrder: string[]): Promise<void> => {
    if (!user?.id) return;
    setLoading(true);
    try {
      const response = await axios.put<TaskSequenceResponse>(`http://localhost:8000/timeline/sequences/${sequenceId}/reorder`, {
        user_id: user.id,
        order: newOrder
      });
      setSequences(prev => prev.map(seq => 
        seq.id === sequenceId ? response.data.sequence : seq
      ));
      setError(null);
    } catch (err) {
      handleError(err as AxiosError<ErrorResponse>, 'reorder sequence');
    } finally {
      setLoading(false);
    }
  }, [user]);

  const predictEnergyLevel = useCallback(async (eventId: string): Promise<number> => {
    if (!user?.id) return 0;
    try {
      const response = await axios.get<TaskPrediction>(`http://localhost:8000/timeline/events/${eventId}/predict-energy`, {
        params: { user_id: user.id }
      });
      return response.data.prediction;
    } catch (err) {
      handleError(err as AxiosError<ErrorResponse>, 'predict energy level');
      return 0;
    }
  }, [user]);

  const predictFocusLevel = useCallback(async (eventId: string): Promise<number> => {
    if (!user?.id) return 0;
    try {
      const response = await axios.get<TaskPrediction>(`http://localhost:8000/timeline/events/${eventId}/predict-focus`, {
        params: { user_id: user.id }
      });
      return response.data.prediction;
    } catch (err) {
      handleError(err as AxiosError<ErrorResponse>, 'predict focus level');
      return 0;
    }
  }, [user]);

  const getEventChain = useCallback(async (eventId: string): Promise<EventChainResponse> => {
    if (!user?.id) return { upstream: [], downstream: [] };
    try {
      const response = await axios.get<EventChainResponse>(`http://localhost:8000/timeline/events/${eventId}/chain`, {
        params: { user_id: user.id }
      });
      return response.data;
    } catch (err) {
      handleError(err as AxiosError<ErrorResponse>, 'get event chain');
      return { upstream: [], downstream: [] };
    }
  }, [user]);

  const analyzeImpact = useCallback(async (eventId: string, change: Partial<TimelineEvent>): Promise<ImpactAnalysisResponse> => {
    if (!user?.id) return { affectedEvents: [], severity: 'low', recommendations: [] };
    try {
      const response = await axios.get<ImpactAnalysisResponse>(`http://localhost:8000/timeline/events/${eventId}/impact`, {
        params: {
          user_id: user.id,
          change: JSON.stringify(change)
        }
      });
      return response.data;
    } catch (err) {
      handleError(err as AxiosError<ErrorResponse>, 'analyze impact');
      return { affectedEvents: [], severity: 'low', recommendations: [] };
    }
  }, [user]);

  const value: TimelineContextType = {
    events,
    stats,
    energyPattern,
    loading,
    error,
    fetchEvents,
    addEvent,
    updateEvent,
    deleteEvent,
    updateEnergyPattern,
    getTimelineStats,
    logFocusMetrics,
    getEnergyForecast,
    sequences,
    conflicts: [],
    createSequence,
    updateSequence,
    deleteSequence,
    addDependency,
    removeDependency,
    validateDependencies,
    detectConflicts,
    resolveConflict,
    optimizeSequence,
    reorderSequence,
    predictEnergyLevel,
    predictFocusLevel,
    getEventChain,
    analyzeImpact
  };

  return (
    <TimelineContext.Provider value={value}>
      {children}
    </TimelineContext.Provider>
  );
};

export const useTimeline = (): TimelineContextType => {
  const context = useContext(TimelineContext);
  if (!context) {
    throw new Error('useTimeline must be used within a TimelineProvider');
  }
  return context;
}; 