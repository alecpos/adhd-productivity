export interface Task {
    id: string;
    title: string;
    description?: string;
    dueDate: Date;
    status: TaskStatus;
    energyLevel: number;
}

export enum TaskStatus {
    TODO = 'TODO',
    IN_PROGRESS = 'IN_PROGRESS',
    COMPLETED = 'COMPLETED'
}

export interface User {
    id: string;
    email: string;
    name: string;
    preferences: UserPreferences;
}

export interface UserPreferences {
    theme: 'light' | 'dark';
    notifications: boolean;
    energyTracking: boolean;
}

export interface EnergyLevel {
    id: string;
    userId: string;
    level: number;
    timestamp: Date;
    notes?: string;
} 