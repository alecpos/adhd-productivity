import { create } from 'zustand';

import type { Task, User, EnergyLevel } from '../types';

interface AppState {
    user: User | null;
    tasks: Task[];
    energyLevels: EnergyLevel[];

    // Actions
    setUser: (user: User | null) => void;
    addTask: (task: Task) => void;
    updateTask: (id: string, updates: Partial<Task>) => void;
    logEnergyLevel: (level: EnergyLevel) => void;
}

export const useStore = create<AppState>((set) => ({
    user: null,
    tasks: [] as Task[],
    energyLevels: [] as EnergyLevel[],

    setUser: (user: User | null) => set({ user }),
    addTask: (task: Task) => set((state) => ({
        tasks: [...state.tasks, task]
    })),
    updateTask: (id: string, updates: Partial<Task>) => set((state) => ({
        tasks: state.tasks.map(task =>
            task.id === id ? { ...task, ...updates } : task
        )
    })),
    logEnergyLevel: (level: EnergyLevel) => set((state) => ({
        energyLevels: [...state.energyLevels, level]
    }))
}));
