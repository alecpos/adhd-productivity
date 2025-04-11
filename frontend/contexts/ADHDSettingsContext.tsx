import React, { createContext, useContext, useState, useCallback } from 'react';

import api from '@/app/services/api';

import { useAuth } from './AuthContext';

interface DistractionSensitivity {
  visual: number;  // 0-10 scale
  auditory: number;
  movement: number;
  internal: number;  // mind wandering, intrusive thoughts
}

interface EnergyManagement {
  peakHours: { start: string; end: string }[];
  lowEnergyPeriods: { start: string; end: string }[];
  energyRecoveryRate: number;  // minutes needed to recover after intense focus
  sustainedFocusLimit: number;  // minutes before needing a break
}

interface ExecutiveFunctionSettings {
  taskInitiationSupport: boolean;
  taskSwitchingAssistance: boolean;
  timeBlindnessCompensation: boolean;
  workingMemoryAids: boolean;
  prioritizationHelp: boolean;
}

interface ADHDProfile {
  distractionSensitivity: DistractionSensitivity;
  energyManagement: EnergyManagement;
  executiveFunction: ExecutiveFunctionSettings;
  medicationSchedule?: {
    times: string[];
    duration: number;  // effect duration in hours
    peakTime: number;  // hours after taking when most effective
  };
  accommodations: {
    needsExternalAccountability: boolean;
    prefersVisualInformation: boolean;
    requiresFrequentBreaks: boolean;
    needsDeadlineBuffer: boolean;
    strugglesWith: string[];
    copingStrategies: string[];
  };
}

interface ADHDMetrics {
  focusScores: {
    daily: number;
    weekly: number;
    monthly: number;
  };
  taskCompletion: {
    onTime: number;
    late: number;
    incomplete: number;
  };
  medicationEffectiveness: number;  // 0-1 score
  productiveHours: {
    hour: number;
    score: number;
  }[];
  distractionPatterns: {
    type: string;
    frequency: number;
    timeOfDay: string;
    impact: number;
  }[];
  energyLevels: {
    timestamp: string;
    level: number;
    activity: string;
  }[];
  focusPatterns: {
    timeOfDay: string;
    duration: number;
    quality: number;
    environment: Record<string, any>;
  }[];
  executiveFunctionMetrics: {
    taskInitiationDelay: number;
    taskSwitchingFrequency: number;
    timeEstimationAccuracy: number;
    workingMemoryUtilization: number;
  };
}

interface ADHDSettingsContextType {
  profile: ADHDProfile | null;
  metrics: ADHDMetrics | null;
  loading: boolean;
  error: string | null;

  // Profile Management
  updateProfile: (updates: Partial<ADHDProfile>) => Promise<void>;
  getMetrics: (startDate: Date, endDate: Date) => Promise<void>;

  // Tracking Functions
  logDistraction: (type: string, duration: number, impact: number, context?: string) => Promise<void>;
  logMedicationEffect: (effectiveness: number, sideEffects?: string[], notes?: string) => Promise<void>;
  logEnergyLevel: (level: number, activity: string) => Promise<void>;
  logFocusSession: (duration: number, quality: number, environment: Record<string, any>) => Promise<void>;
  logExecutiveFunction: (metrics: Partial<ADHDMetrics['executiveFunctionMetrics']>) => Promise<void>;

  // Analysis Functions
  getRecommendations: () => Promise<{
    scheduling: string[];
    environment: string[];
    strategies: string[];
    accommodations: string[];
  }>;

  analyzePatterns: () => Promise<{
    productivity: { time: string; score: number }[];
    distractions: { trigger: string; frequency: number }[];
    successFactors: { factor: string; impact: number }[];
    energyFlow: { time: string; level: number; activity: string }[];
    focusQuality: { time: string; duration: number; quality: number }[];
  }>;

  // Planning Functions
  generateDailyPlan: (date: Date) => Promise<{
    medicationTiming: string[];
    breakSchedule: { time: string; duration: number }[];
    focusBlocks: { start: string; end: string; type: string }[];
    accommodations: string[];
    energyForecast: { time: string; level: number }[];
    contingencyPlans: { trigger: string; action: string }[];
  }>;

  // Calibration Functions
  calibrateSettings: () => Promise<{
    suggestedUpdates: Partial<ADHDProfile>;
    reasoning: string[];
    confidenceScore: number;
    dataPoints: number;
  }>;
}

const ADHDSettingsContext = createContext<ADHDSettingsContextType | undefined>(undefined);

export const ADHDSettingsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [profile, setProfile] = useState<ADHDProfile | null>(null);
  const [metrics, setMetrics] = useState<ADHDMetrics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();

  const handleError = (err: any, operation: string) => {
    console.error(`Error in ADHDSettings ${operation}:`, err);
    const errorMessage = err.response?.data?.detail || `Failed to ${operation}`;
    setError(errorMessage);
    return null;
  };

  const updateProfile = useCallback(async (updates: Partial<ADHDProfile>) => {
    if (!user) return;
    setLoading(true);
    try {
      const response = await api.patch(`/adhd-settings/profile/${user.id}`, updates);
      setProfile(response.data);
      setError(null);
    } catch (err) {
      handleError(err, 'update profile');
    } finally {
      setLoading(false);
    }
  }, [user]);

  const getMetrics = useCallback(async (startDate: Date, endDate: Date) => {
    if (!user) return;
    setLoading(true);
    try {
      const response = await api.get(`/adhd-settings/metrics/${user.id}`, {
        params: {
          start_date: startDate.toISOString(),
          end_date: endDate.toISOString()
        }
      });
      setMetrics(response.data);
      setError(null);
    } catch (err) {
      handleError(err, 'get metrics');
    } finally {
      setLoading(false);
    }
  }, [user]);

  const logDistraction = useCallback(async (type: string, duration: number, impact: number, context?: string) => {
    if (!user) return;
    setLoading(true);
    try {
      await api.post(`/adhd-settings/distractions/${user.id}`, {
        type,
        duration,
        impact,
        timestamp: new Date().toISOString(),
        context
      });
      setError(null);
    } catch (err) {
      handleError(err, 'log distraction');
    } finally {
      setLoading(false);
    }
  }, [user]);

  const logMedicationEffect = useCallback(async (effectiveness: number, sideEffects?: string[], notes?: string) => {
    if (!user) return;
    setLoading(true);
    try {
      await api.post(`/adhd-settings/medication/${user.id}`, {
        effectiveness,
        side_effects: sideEffects,
        timestamp: new Date().toISOString(),
        notes
      });
      setError(null);
    } catch (err) {
      handleError(err, 'log medication effect');
    } finally {
      setLoading(false);
    }
  }, [user]);

  const logEnergyLevel = useCallback(async (level: number, activity: string) => {
    if (!user) return;
    setLoading(true);
    try {
      await api.post(`/adhd-settings/energy-levels/${user.id}`, {
        level,
        activity,
        timestamp: new Date().toISOString()
      });
      setError(null);
    } catch (err) {
      handleError(err, 'log energy level');
    } finally {
      setLoading(false);
    }
  }, [user]);

  const logFocusSession = useCallback(async (duration: number, quality: number, environment: Record<string, any>) => {
    if (!user) return;
    setLoading(true);
    try {
      await api.post(`/adhd-settings/focus-sessions/${user.id}`, {
        duration,
        quality,
        environment,
        timestamp: new Date().toISOString()
      });
      setError(null);
    } catch (err) {
      handleError(err, 'log focus session');
    } finally {
      setLoading(false);
    }
  }, [user]);

  const logExecutiveFunction = useCallback(async (metrics: Partial<ADHDMetrics['executiveFunctionMetrics']>) => {
    if (!user) return;
    setLoading(true);
    try {
      await api.post(`/adhd-settings/executive-function/${user.id}`, metrics);
      setError(null);
    } catch (err) {
      handleError(err, 'log executive function');
    } finally {
      setLoading(false);
    }
  }, [user]);

  const getRecommendations = useCallback(async () => {
    if (!user) return {
      strategies: [],
      environment: [],
      scheduling: [],
      accommodations: []
    };

    setLoading(true);
    try {
      const response = await api.get(`/adhd-settings/recommendations/${user.id}`);
      setError(null);
      return response.data;
    } catch (err) {
      handleError(err, 'get recommendations');
      return {
        strategies: [],
        environment: [],
        scheduling: [],
        accommodations: []
      };
    } finally {
      setLoading(false);
    }
  }, [user]);

  const analyzePatterns = useCallback(async () => {
    if (!user) return {
      productivity: [],
      distractions: [],
      successFactors: [],
      energyFlow: [],
      focusQuality: []
    };
    setLoading(true);
    try {
      const response = await api.get(`/adhd-settings/patterns/${user.id}`);
      setError(null);
      return response.data;
    } catch (err) {
      handleError(err, 'analyze patterns');
      return {
        productivity: [],
        distractions: [],
        successFactors: [],
        energyFlow: [],
        focusQuality: []
      };
    } finally {
      setLoading(false);
    }
  }, [user]);

  const generateDailyPlan = useCallback(async (date: Date) => {
    if (!user) return {
      medicationTiming: [],
      breakSchedule: [],
      focusBlocks: [],
      accommodations: [],
      energyForecast: [],
      contingencyPlans: []
    };

    setLoading(true);
    try {
      const response = await api.post(`/adhd-settings/daily-plan/${user.id}`, {
        date: date.toISOString()
      });
      setError(null);
      return response.data;
    } catch (err) {
      handleError(err, 'generate daily plan');
      return {
        medicationTiming: [],
        breakSchedule: [],
        focusBlocks: [],
        accommodations: [],
        energyForecast: [],
        contingencyPlans: []
      };
    } finally {
      setLoading(false);
    }
  }, [user]);

  const calibrateSettings = useCallback(async () => {
    if (!user) return {
      suggestedUpdates: {},
      reasoning: [],
      confidenceScore: 0,
      dataPoints: 0
    };
    setLoading(true);
    try {
      const response = await api.post(`/adhd-settings/calibrate/${user.id}`);
      setError(null);
      return response.data;
    } catch (err) {
      handleError(err, 'calibrate settings');
      return {
        suggestedUpdates: {},
        reasoning: [],
        confidenceScore: 0,
        dataPoints: 0
      };
    } finally {
      setLoading(false);
    }
  }, [user]);

  return (
    <ADHDSettingsContext.Provider value={{
      profile,
      metrics,
      loading,
      error,
      updateProfile,
      getMetrics,
      logDistraction,
      logMedicationEffect,
      logEnergyLevel,
      logFocusSession,
      logExecutiveFunction,
      getRecommendations,
      analyzePatterns,
      generateDailyPlan,
      calibrateSettings,
    }}>
      {children}
    </ADHDSettingsContext.Provider>
  );
};

export const useADHDSettings = () => {
  const context = useContext(ADHDSettingsContext);
  if (context === undefined) {
    throw new Error('useADHDSettings must be used within an ADHDSettingsProvider');
  }
  return context;
};
