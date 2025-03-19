import React, { createContext, useContext, useState, useCallback } from 'react';

import axios from 'axios';

import { useAuth } from './AuthContext';

interface TimeBlock {
  id: string;
  startTime: Date;
  endTime: Date;
  taskId?: string;
  type: 'task' | 'break' | 'focus' | 'buffer';
  energyLevel: 'high' | 'medium' | 'low';
  focusLevel: 'high' | 'medium' | 'low';
  isConflicting: boolean;
  conflictReason?: string;
  metadata?: {
    isOptimal: boolean;
    alternativeSlots?: { startTime: Date; endTime: Date; score: number }[];
    breakType?: 'short' | 'long' | 'lunch';
    energyAlignment: number; // 0-1 score of how well this aligns with energy pattern
    focusRequirement: number; // 0-1 score of required focus
  };
}

interface ScheduleStats {
  totalTasks: number;
  completedTasks: number;
  averageEnergyLevel: number;
  focusTimePercentage: number;
  breakTimePercentage: number;
  taskCompletionRate: number;
  energyUtilization: number;
  focusEfficiency: number;
  conflictRate: number;
  averageTaskDuration: number;
  mostProductiveTimeSlots: { hour: number; productivity: number }[];
}

interface EnergyConstraint {
  taskId: string;
  minEnergy: number;
  maxEnergy: number;
  preferredEnergy: number;
  flexibility: number;
}

interface FocusConstraint {
  taskId: string;
  minFocus: number;
  maxFocus: number;
  preferredFocus: number;
  flexibility: number;
}

interface OptimizationConstraints {
  energy: EnergyConstraint[];
  focus: FocusConstraint[];
  dependencies: {
    taskId: string;
    dependsOn: string[];
    type: 'strict' | 'flexible';
  }[];
  timePreferences: {
    taskId: string;
    preferredTimes: { start: string; end: string }[];
    weight: number;
  }[];
}

interface OptimizationRequest {
  startTime: Date;
  endTime: Date;
  tasks: string[];
  preferences?: {
    breakFrequency?: number;
    focusBlockDuration?: number;
    energyConstraints?: {
      [key: string]: 'high' | 'medium' | 'low';
    };
    priorityWeights?: {
      energy: number;
      focus: number;
      deadline: number;
      preference: number;
    };
    workingHours?: {
      [key: string]: { start: string; end: string }; // key is day of week (0-6)
    };
    breakPreferences?: {
      minDuration: number;
      maxDuration: number;
      preferredTimes?: string[]; // HH:mm format
    };
    conflictResolution?: 'strict' | 'flexible' | 'ignore';
  };
  constraints?: OptimizationConstraints;
  learningRate?: number;
  maxIterations?: number;
  convergenceThreshold?: number;
  optimizationStrategy?: 'balanced' | 'energy_focused' | 'time_focused' | 'focus_focused';
  adaptiveScheduling?: {
    enabled: boolean;
    sensitivity: number;
    learningPeriod: number;
  };
}

interface ConflictResolution {
  blockId: string;
  resolution: 'move' | 'split' | 'remove';
  newStartTime?: Date;
  newEndTime?: Date;
}

interface OptimizationResult {
  schedule: TimeBlock[];
  conflicts: {
    id: string;
    type: 'energy' | 'focus' | 'time' | 'preference';
    description: string;
    suggestedResolutions: {
      type: 'move' | 'split' | 'remove';
      impact: number;
      newTimes?: { startTime: Date; endTime: Date }[];
    }[];
  }[];
  metrics: {
    energyAlignment: number;
    focusOptimization: number;
    breakDistribution: number;
    conflictCount: number;
    overallScore: number;
  };
  optimizationMetrics: {
    iterationCount: number;
    convergenceScore: number;
    constraintSatisfaction: {
      energy: number;
      focus: number;
      time: number;
      dependencies: number;
    };
    improvement: {
      overall: number;
      byMetric: {
        energy: number;
        focus: number;
        time: number;
        dependencies: number;
      };
    };
  };
  alternativeSchedules: {
    blocks: TimeBlock[];
    score: number;
    tradeoffs: {
      metric: string;
      difference: number;
    }[];
  }[];
}

interface ScheduleOptimizerContextType {
  currentSchedule: TimeBlock[];
  scheduleStats: ScheduleStats | null;
  optimizationResult: OptimizationResult | null;
  loading: boolean;
  error: string | null;
  optimizeSchedule: (request: OptimizationRequest) => Promise<void>;
  getScheduleStats: (userId: string) => Promise<void>;
  scheduleBlocks: (request: OptimizationRequest) => Promise<void>;
  resolveConflict: (resolution: ConflictResolution) => Promise<void>;
  adjustSchedule: (blockId: string, adjustments: Partial<TimeBlock>) => Promise<void>;
  reoptimizeSegment: (startTime: Date, endTime: Date) => Promise<void>;
  getAlternativeSlots: (taskId: string) => Promise<{ startTime: Date; endTime: Date; score: number }[]>;
  optimizationConstraints: OptimizationConstraints | null;
  setOptimizationConstraints: (constraints: OptimizationConstraints) => void;
  validateConstraints: (constraints: OptimizationConstraints) => Promise<{
    valid: boolean;
    issues: string[];
    suggestions: string[];
  }>;
  generateAlternativeSchedules: (count: number) => Promise<{
    schedules: TimeBlock[][];
    scores: number[];
  }>;
  analyzeScheduleQuality: (schedule: TimeBlock[]) => Promise<{
    score: number;
    breakdown: {
      energyAlignment: number;
      focusOptimization: number;
      timeEfficiency: number;
      constraintSatisfaction: number;
    };
    improvements: string[];
  }>;
  compareSchedules: (schedule1: TimeBlock[], schedule2: TimeBlock[]) => Promise<{
    differences: {
      block: TimeBlock;
      type: 'moved' | 'added' | 'removed' | 'modified';
      impact: number;
    }[];
    overallDifference: number;
    recommendation: string;
  }>;
  optimizeForMetric: (metric: 'energy' | 'focus' | 'time' | 'balance') => Promise<void>;
  getOptimizationInsights: () => Promise<{
    patterns: {
      description: string;
      frequency: number;
      impact: number;
    }[];
    bottlenecks: {
      type: string;
      description: string;
      affectedTasks: string[];
      suggestions: string[];
    }[];
    recommendations: {
      short_term: string[];
      long_term: string[];
    };
  }>;
}

const ScheduleOptimizerContext = createContext<ScheduleOptimizerContextType | undefined>(undefined);

export const ScheduleOptimizerProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentSchedule, setCurrentSchedule] = useState<TimeBlock[]>([]);
  const [scheduleStats, setScheduleStats] = useState<ScheduleStats | null>(null);
  const [optimizationResult, setOptimizationResult] = useState<OptimizationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();
  const [optimizationConstraints, setOptimizationConstraints] = useState<OptimizationConstraints | null>(null);

  const handleError = (err: any, operation: string) => {
    console.error(`Error in ScheduleOptimizer ${operation}:`, err);
    setError(err.response?.data?.detail || `Failed to ${operation}`);
    throw err;
  };

  const optimizeSchedule = useCallback(async (request: OptimizationRequest) => {
    if (!user) return;
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/schedule/optimize', {
        ...request,
        user_id: user.id
      });
      setCurrentSchedule(response.data.schedule);
      setOptimizationResult(response.data);
      setError(null);
    } catch (err) {
      handleError(err, 'optimize schedule');
    } finally {
      setLoading(false);
    }
  }, [user]);

  const getScheduleStats = useCallback(async (userId: string) => {
    if (!user) return;
    setLoading(true);
    try {
      const response = await axios.get(`http://localhost:8000/schedule/stats/${userId}`);
      setScheduleStats(response.data);
      setError(null);
    } catch (err) {
      handleError(err, 'fetch schedule stats');
    } finally {
      setLoading(false);
    }
  }, [user]);

  const scheduleBlocks = useCallback(async (request: OptimizationRequest) => {
    if (!user) return;
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/schedule/blocks', {
        ...request,
        user_id: user.id
      });
      setCurrentSchedule(response.data.blocks);
      setError(null);
    } catch (err) {
      handleError(err, 'schedule blocks');
    } finally {
      setLoading(false);
    }
  }, [user]);

  const resolveConflict = useCallback(async (resolution: ConflictResolution) => {
    if (!user) return;
    setLoading(true);
    try {
      const response = await axios.post(`http://localhost:8000/schedule/resolve-conflict`, {
        user_id: user.id,
        resolution
      });
      setCurrentSchedule(response.data.schedule);
      setOptimizationResult(response.data);
      setError(null);
    } catch (err) {
      handleError(err, 'resolve conflict');
    } finally {
      setLoading(false);
    }
  }, [user]);

  const adjustSchedule = useCallback(async (blockId: string, adjustments: Partial<TimeBlock>) => {
    if (!user) return;
    setLoading(true);
    try {
      const response = await axios.put(`http://localhost:8000/schedule/blocks/${blockId}`, {
        user_id: user.id,
        ...adjustments
      });
      setCurrentSchedule(prev => prev.map(block => 
        block.id === blockId ? { ...block, ...response.data } : block
      ));
      setError(null);
    } catch (err) {
      handleError(err, 'adjust schedule');
    } finally {
      setLoading(false);
    }
  }, [user]);

  const reoptimizeSegment = useCallback(async (startTime: Date, endTime: Date) => {
    if (!user) return;
    setLoading(true);
    try {
      const response = await axios.post(`http://localhost:8000/schedule/reoptimize-segment`, {
        user_id: user.id,
        start_time: startTime.toISOString(),
        end_time: endTime.toISOString()
      });
      setCurrentSchedule(response.data.schedule);
      setOptimizationResult(response.data);
      setError(null);
    } catch (err) {
      handleError(err, 'reoptimize segment');
    } finally {
      setLoading(false);
    }
  }, [user]);

  const getAlternativeSlots = useCallback(async (taskId: string) => {
    if (!user) return [];
    setLoading(true);
    try {
      const response = await axios.get(`http://localhost:8000/schedule/alternative-slots/${taskId}`, {
        params: { user_id: user.id }
      });
      setError(null);
      return response.data;
    } catch (err) {
      handleError(err, 'get alternative slots');
      return [];
    } finally {
      setLoading(false);
    }
  }, [user]);

  const validateConstraints = useCallback(async (constraints: OptimizationConstraints) => {
    if (!user) return { valid: false, issues: ['User not authenticated'], suggestions: [] };
    setLoading(true);
    try {
      const response = await axios.post(`http://localhost:8000/schedule/validate-constraints`, {
        user_id: user.id,
        constraints
      });
      setError(null);
      return response.data;
    } catch (err) {
      handleError(err, 'validate constraints');
      return { valid: false, issues: ['Validation failed'], suggestions: [] };
    } finally {
      setLoading(false);
    }
  }, [user]);

  const generateAlternativeSchedules = useCallback(async (count: number) => {
    if (!user) return { schedules: [], scores: [] };
    setLoading(true);
    try {
      const response = await axios.post(`http://localhost:8000/schedule/alternatives`, {
        user_id: user.id,
        count
      });
      setError(null);
      return response.data;
    } catch (err) {
      handleError(err, 'generate alternatives');
      return { schedules: [], scores: [] };
    } finally {
      setLoading(false);
    }
  }, [user]);

  const analyzeScheduleQuality = useCallback(async (schedule: TimeBlock[]) => {
    if (!user) return {
      score: 0,
      breakdown: { energyAlignment: 0, focusOptimization: 0, timeEfficiency: 0, constraintSatisfaction: 0 },
      improvements: []
    };
    setLoading(true);
    try {
      const response = await axios.post(`http://localhost:8000/schedule/analyze-quality`, {
        user_id: user.id,
        schedule
      });
      setError(null);
      return response.data;
    } catch (err) {
      handleError(err, 'analyze quality');
      return {
        score: 0,
        breakdown: { energyAlignment: 0, focusOptimization: 0, timeEfficiency: 0, constraintSatisfaction: 0 },
        improvements: []
      };
    } finally {
      setLoading(false);
    }
  }, [user]);

  const compareSchedules = useCallback(async (schedule1: TimeBlock[], schedule2: TimeBlock[]) => {
    if (!user) return { differences: [], overallDifference: 0, recommendation: '' };
    setLoading(true);
    try {
      const response = await axios.post(`http://localhost:8000/schedule/compare`, {
        user_id: user.id,
        schedule1,
        schedule2
      });
      setError(null);
      return response.data;
    } catch (err) {
      handleError(err, 'compare schedules');
      return { differences: [], overallDifference: 0, recommendation: '' };
    } finally {
      setLoading(false);
    }
  }, [user]);

  const optimizeForMetric = useCallback(async (metric: 'energy' | 'focus' | 'time' | 'balance') => {
    if (!user) return;
    setLoading(true);
    try {
      const response = await axios.post(`http://localhost:8000/schedule/optimize-metric`, {
        user_id: user.id,
        metric
      });
      setCurrentSchedule(response.data.schedule);
      setOptimizationResult(response.data);
      setError(null);
    } catch (err) {
      handleError(err, 'optimize for metric');
    } finally {
      setLoading(false);
    }
  }, [user]);

  const getOptimizationInsights = useCallback(async () => {
    if (!user) return {
      patterns: [],
      bottlenecks: [],
      recommendations: { short_term: [], long_term: [] }
    };
    setLoading(true);
    try {
      const response = await axios.get(`http://localhost:8000/schedule/insights`, {
        params: { user_id: user.id }
      });
      setError(null);
      return response.data;
    } catch (err) {
      handleError(err, 'get optimization insights');
      return {
        patterns: [],
        bottlenecks: [],
        recommendations: { short_term: [], long_term: [] }
      };
    } finally {
      setLoading(false);
    }
  }, [user]);

  return (
    <ScheduleOptimizerContext.Provider value={{
      currentSchedule,
      scheduleStats,
      optimizationResult,
      loading,
      error,
      optimizeSchedule,
      getScheduleStats,
      scheduleBlocks,
      resolveConflict,
      adjustSchedule,
      reoptimizeSegment,
      getAlternativeSlots,
      optimizationConstraints,
      setOptimizationConstraints,
      validateConstraints,
      generateAlternativeSchedules,
      analyzeScheduleQuality,
      compareSchedules,
      optimizeForMetric,
      getOptimizationInsights,
    }}>
      {children}
    </ScheduleOptimizerContext.Provider>
  );
};

export const useScheduleOptimizer = () => {
  const context = useContext(ScheduleOptimizerContext);
  if (context === undefined) {
    throw new Error('useScheduleOptimizer must be used within a ScheduleOptimizerProvider');
  }
  return context;
}; 