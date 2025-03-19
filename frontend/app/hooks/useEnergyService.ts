import { useState, useCallback } from 'react';

import { api } from '@/lib/api';

import { useAuth } from '../../contexts/AuthContext';

interface EnergyLog {
    id: string;
    userId: string;
    energy_level: number;
    timestamp: string;
    notes?: string;
    taskId?: string;
    activityType?: string;
}

interface EnergyPattern {
    hourly_patterns: {
        [hour: string]: {
            average: number;
            std_dev: number;
            stability: number;
            sample_size: number;
            min: number;
            max: number;
        };
    };
    daily_patterns: {
        [day: string]: {
            average: number;
            std_dev: number;
            sample_size: number;
            time_distribution: {
                morning: number;
                afternoon: number;
                evening: number;
            };
        };
    };
    energy_transitions: Record<string, any>;
    variability_metrics: {
        overall_variability: number;
        trend_strength: number;
        cyclical_pattern_strength: number;
    };
    optimization_suggestions: Array<{
        type: string;
        message: string;
        action_items: string[];
    }>;
}

interface EnergyAnalytics {
    baseline_metrics: {
        average_energy: number;
        energy_stability: number;
        time_distribution: {
            morning: number;
            afternoon: number;
            evening: number;
        };
        peak_performance_window: any;
    };
    stability_analysis: {
        metrics: {
            overall_stability: number;
            day_to_day_variation: number;
            intraday_variation: number;
        };
        patterns: Array<{
            pattern: string;
            description: string;
            impact: string;
            suggestions: string[];
        }>;
        trend_analysis: any;
    };
    recovery_metrics: {
        average_recovery_rate: number;
        recovery_patterns: Array<{
            duration: number;
            total_recovery: number;
            efficiency: number;
        }>;
        recovery_efficiency: number;
        optimization_suggestions: any[];
    };
    productivity_correlation: {
        correlation: {
            priority: number;
            complexity: number;
        } | null;
        patterns: Array<{
            type: string;
            description: string;
            strength: number;
        }>;
        recommendations: string[];
    };
    insights: Array<{
        category: string;
        insight: string;
        impact: string;
        recommendations: string[];
    }>;
    optimization_score: {
        overall_score: number;
        component_scores: {
            baseline: number;
            stability: number;
            recovery: number;
            productivity: number;
        };
        optimization_level: string;
        focus_areas: string[];
    };
}

export function useEnergyService() {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const { user } = useAuth();

    const handleRequest = async <T>(request: () => Promise<T>): Promise<T | null> => {
        setLoading(true);
        setError(null);
        try {
            const result = await request();
            return result;
        } catch (err: any) {
            setError(err.message || 'An error occurred');
            return null;
        } finally {
            setLoading(false);
        }
    };

    const logEnergy = useCallback(async (data: Omit<EnergyLog, 'id' | 'userId' | 'timestamp'>) => {
        if (!user?.id) throw new Error('User not authenticated');
        return handleRequest(async () => {
            const response = await api.post<EnergyLog>('/api/energy/log', {
                ...data,
                userId: user.id,
                timestamp: new Date().toISOString()
            });
            return response.data;
        });
    }, [user?.id]);

    const getEnergyLogs = useCallback(async (days: number = 30) => {
        if (!user?.id) throw new Error('User not authenticated');
        return handleRequest(async () => {
            const response = await api.get<EnergyLog[]>('/api/energy/logs', {
                params: { userId: user.id, days }
            });
            return response.data;
        });
    }, [user?.id]);

    const getEnergyPatterns = useCallback(async (days: number = 30) => {
        if (!user?.id) throw new Error('User not authenticated');
        return handleRequest(async () => {
            const response = await api.get<EnergyPattern>('/api/energy/patterns', {
                params: { userId: user.id, days }
            });
            return response.data;
        });
    }, [user?.id]);

    const getEnergyAnalytics = useCallback(async () => {
        if (!user?.id) throw new Error('User not authenticated');
        return handleRequest(async () => {
            const response = await api.get<EnergyAnalytics>('/api/energy/analytics', {
                params: { userId: user.id }
            });
            return response.data;
        });
    }, [user?.id]);

    const getPeakHours = useCallback(async (days: number = 30) => {
        if (!user?.id) throw new Error('User not authenticated');
        return handleRequest(async () => {
            const response = await api.get<Array<{ hour: number; average_energy: number }>>('/api/energy/peak-hours', {
                params: { userId: user.id, days }
            });
            return response.data;
        });
    }, [user?.id]);

    const getEnergyInsights = useCallback(async () => {
        if (!user?.id) throw new Error('User not authenticated');
        return handleRequest(async () => {
            const response = await api.get<{
                optimal_energy_levels: number[];
                completion_rates: Array<{
                    energy_level: number;
                    completion_rate: number;
                    total_tasks: number;
                }>;
                recommendations: string[];
            }>('/api/energy/insights', {
                params: { userId: user.id }
            });
            return response.data;
        });
    }, [user?.id]);

    const batchLogEnergy = useCallback(async (data: Array<Omit<EnergyLog, 'id' | 'userId' | 'timestamp'>>) => {
        if (!user?.id) throw new Error('User not authenticated');
        return handleRequest(async () => {
            const response = await api.post<EnergyLog[]>('/api/energy/batch-log', {
                userId: user.id,
                logs: data.map(log => ({
                    ...log,
                    timestamp: new Date().toISOString()
                }))
            });
            return response.data;
        });
    }, [user?.id]);

    const getUserEnergyData = useCallback(async (date: Date) => {
        if (!user?.id) throw new Error('User not authenticated');
        return handleRequest(async () => {
            const [patterns, analytics] = await Promise.all([
                getEnergyPatterns(),
                getEnergyAnalytics()
            ]);

            const hourStr = date.getHours().toString();
            const hourPattern = patterns?.hourly_patterns[hourStr];
            const dayPattern = patterns?.daily_patterns[date.toLocaleDateString('en-US', { weekday: 'long' })];

            return {
                patterns,
                analytics,
                date,
                energy_level: hourPattern?.average || 0,
                optimal_hours: Object.entries(patterns?.hourly_patterns || {})
                    .filter(([_, data]) => data.average >= 7)
                    .map(([hour]) => `${hour}:00`),
                recovery_needed: (analytics?.recovery_metrics?.recovery_efficiency ?? 1) < 0.5,
                current_stability: hourPattern?.stability || 0,
                day_pattern: dayPattern,
                recommendations: analytics?.insights
                    ?.filter(insight => insight.category === 'recovery')
                    ?.map(insight => insight.recommendations)
                    ?.flat() || []
            };
        });
    }, [user?.id, getEnergyPatterns, getEnergyAnalytics]);

    return {
        loading,
        error,
        logEnergy,
        getEnergyLogs,
        getEnergyPatterns,
        getEnergyAnalytics,
        getPeakHours,
        getEnergyInsights,
        batchLogEnergy,
        getUserEnergyData
    };
} 