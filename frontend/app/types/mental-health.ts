import { UUID } from '@/app/types/common';

export enum MoodLevel {
    VeryLow = 1,
    Low = 2,
    Moderate = 3,
    High = 4,
    VeryHigh = 5
}

export enum StressLevel {
    None = 0,
    Low = 1,
    Moderate = 2,
    High = 3,
    Extreme = 4
}

export enum AnxietyLevel {
    None = 0,
    Low = 1,
    Moderate = 2,
    High = 3,
    Extreme = 4
}

export interface EmotionResult {
    label: string;
    score: number;
}

export interface CreateMentalHealthLog {
    userId: string;
    moodScore: number;
    energyLevel?: number;
    stressLevel: number;
    anxietyLevel: number;
    focusLevel: number;
    notes?: string;
    sentimentScore?: number | null;
    aiRecommendations?: string[] | null;
    sleepQuality?: number | null;
    activityLog?: string[] | null;
}

export interface MentalHealthLog {
    id: string;
    userId: string;
    moodScore: number;
    stressLevel: number;
    anxietyLevel: number;
    focusLevel: number;
    notes?: string;
    aiRecommendations?: string[];
    sleepQuality?: number;
    energyLevel?: number;
    activityLog?: string[];
    createdAt: string;
    updatedAt: string;
}

export interface MentalHealthTrends {
    moodTrend: {
        date: string;
        score: number;
    }[];
    stressTrend: {
        date: string;
        level: number;
    }[];
    anxietyTrend: {
        date: string;
        level: number;
    }[];
    energyTrend?: {
        date: string;
        level: number;
    }[];
    sleepTrend?: {
        date: string;
        quality: number;
    }[];
}

export interface MoodLog {
    date: string;
    mood: number;
    notes: string | null;
}

export interface MentalHealthStats {
    mood_average: number;
    total_logs: number;
    recent_moods: MoodLog[];
    streak: number;
}

export interface MentalHealthInsights {
    averageMood: number;
    averageStress: number;
    averageAnxiety: number;
    sentimentScore: number;
    dominantEmotion: EmotionResult;
    stressIndicators: string[];
    moodPatterns: {
        timeOfDay: {
            morning: number;
            afternoon: number;
            evening: number;
        };
        dayOfWeek: {
            [key: string]: number;
        };
    };
    correlations: {
        sleepQuality?: number;
        energyLevel?: number;
        activities?: {
            [activity: string]: number;
        };
    };
    recommendations: string[];
}

export interface CopingStrategy {
    id: string;
    name: string;
    description: string;
    category: string;
    effectiveness: number;
    timeRequired: number;
    energyRequired: number;
    tags: string[];
}

export interface FollowUpResponse {
    questionId: string;
    response: string;
    timestamp?: string;
}

export interface FollowUpQuestion {
    id: string;
    question: string;
    questionText: string;
    type: 'moodDrop' | 'scheduleAdjustment' | 'energyLevel' | 'custom' | 'text';
    response?: string;
    timestamp?: string;
    context?: string;
    triggerCondition?: {
        field: string;
        operator: 'lt' | 'gt' | 'eq';
        value: number;
    };
}

export type TimePeriod = 'day' | 'week' | 'month' | 'year';

export function getMoodLevelLabel(score: number): MoodLevel {
    if (score <= 3) return MoodLevel.Low;
    if (score <= 7) return MoodLevel.Moderate;
    return MoodLevel.High;
}

export function getStressLevelLabel(level: number): StressLevel {
    if (level <= 3) return StressLevel.Low;
    if (level <= 7) return StressLevel.Moderate;
    return StressLevel.High;
}

export function getAnxietyLevelLabel(level: number): AnxietyLevel {
    if (level <= 3) return AnxietyLevel.Low;
    if (level <= 7) return AnxietyLevel.Moderate;
    return AnxietyLevel.High;
}

export interface MentalHealthService {
    getStats: (userId: string) => Promise<MentalHealthStats>;
}

export default {
    MoodLevel,
    StressLevel,
    AnxietyLevel,
    getMoodLevelLabel,
    getStressLevelLabel,
    getAnxietyLevelLabel,
}; 