import { useState, useCallback } from 'react';

import { mentalHealthService } from '@/app/services/mental-health';
import {
    MentalHealthTrends,
    MentalHealthInsights,
    MentalHealthStats,
    CopingStrategy
} from '@/app/types/mental-health';

import { useAuth } from '../../contexts/AuthContext';

interface MentalHealthLog {
    id: string;
    userId: string;
    createdAt: string;
    moodScore: number;
    stressLevel: number;
    anxietyLevel: number;
    focusLevel: number;
    notes?: string;
    activities?: string[];
    sleepQuality?: number;
    energyLevel?: number;
}

export function useMentalHealthService() {
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

    const createLog = useCallback(async (data: Partial<MentalHealthLog>) => {
        if (!user?.id) throw new Error('User not authenticated');
        return handleRequest(() => mentalHealthService.createLog({
            ...data,
            userId: user.id
        }));
    }, [user?.id]);

    const logMood = useCallback(async (data: any) => {
        if (!user?.id) throw new Error('User not authenticated');
        return handleRequest(() => mentalHealthService.logMood({
            ...data,
            userId: user.id
        }));
    }, [user?.id]);

    const getLogs = useCallback(async () => {
        if (!user?.id) throw new Error('User not authenticated');
        return handleRequest(() => mentalHealthService.getLogs(user.id));
    }, [user?.id]);

    const getMoodHistory = useCallback(async () => {
        if (!user?.id) throw new Error('User not authenticated');
        return handleRequest(() => mentalHealthService.getMoodHistory());
    }, [user?.id]);

    const getTrends = useCallback(async (period: string) => {
        if (!user?.id) throw new Error('User not authenticated');
        return handleRequest(() => mentalHealthService.getTrends(period));
    }, [user?.id]);

    const getInsights = useCallback(async () => {
        if (!user?.id) throw new Error('User not authenticated');
        return handleRequest(() => mentalHealthService.getInsights(user.id));
    }, [user?.id]);

    const getStats = useCallback(async () => {
        if (!user?.id) throw new Error('User not authenticated');
        return handleRequest(() => mentalHealthService.getStats(user.id));
    }, [user?.id]);

    const analyzeMood = useCallback(async (text: string) => {
        return handleRequest(() => mentalHealthService.analyzeMood(text));
    }, []);

    const getRecommendations = useCallback(async (data: { mood: string; notes?: string }) => {
        return handleRequest(() => mentalHealthService.getRecommendations(data));
    }, []);

    const getCopingStrategies = useCallback(async () => {
        return handleRequest(() => mentalHealthService.getCopingStrategies());
    }, []);

    // Additional utility functions
    const getMoodTrend = useCallback(async (days: number = 7) => {
        const logs = await getLogs();
        if (!logs) return null;

        const recentLogs = logs
            .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
            .slice(0, days);

        return {
            trend: recentLogs.map(log => ({
                date: log.createdAt,
                mood: log.moodScore,
                stress: log.stressLevel,
                anxiety: log.anxietyLevel,
                focus: log.focusLevel
            })),
            average: {
                mood: recentLogs.reduce((acc, log) => acc + log.moodScore, 0) / recentLogs.length,
                stress: recentLogs.reduce((acc, log) => acc + log.stressLevel, 0) / recentLogs.length,
                anxiety: recentLogs.reduce((acc, log) => acc + log.anxietyLevel, 0) / recentLogs.length,
                focus: recentLogs.reduce((acc, log) => acc + log.focusLevel, 0) / recentLogs.length
            }
        };
    }, [getLogs]);

    const getWeeklyInsights = useCallback(async () => {
        const [trends, insights, stats] = await Promise.all([
            getTrends('week'),
            getInsights(),
            getStats()
        ]);

        return {
            trends,
            insights,
            stats,
            summary: {
                weeklyProgress: stats?.total_logs ? (stats.mood_average / 10) * 100 : 0,
                topStressors: insights?.stressIndicators || [],
                recommendations: insights?.recommendations || []
            }
        };
    }, [getTrends, getInsights, getStats]);

    const getDailyMetrics = useCallback(async (date: Date) => {
        if (!user?.id) throw new Error('User not authenticated');
        return handleRequest(async () => {
            const [stats, insights] = await Promise.all([
                getStats(),
                getInsights()
            ]);

            // Get logs for the specific date
            const logs = await getLogs();
            const dayLogs = logs?.filter(log => 
                new Date(log.createdAt).toDateString() === date.toDateString()
            ) || [];

            const averages = dayLogs.reduce((acc, log) => ({
                mood_score: acc.mood_score + (log.moodScore || 0),
                stress_level: acc.stress_level + (log.stressLevel || 0),
                focus_level: acc.focus_level + (log.focusLevel || 0),
                count: acc.count + 1
            }), { mood_score: 0, stress_level: 0, focus_level: 0, count: 0 });

            const count = averages.count || 1;
            return {
                stats,
                insights,
                date,
                mood_score: averages.mood_score / count,
                stress_level: averages.stress_level / count,
                focus_level: averages.focus_level / count
            };
        });
    }, [user?.id, getStats, getInsights, getLogs]);

    return {
        loading,
        error,
        createLog,
        logMood,
        getLogs,
        getMoodHistory,
        getTrends,
        getInsights,
        getStats,
        analyzeMood,
        getRecommendations,
        getCopingStrategies,
        getMoodTrend,
        getWeeklyInsights,
        getDailyMetrics
    };
} 