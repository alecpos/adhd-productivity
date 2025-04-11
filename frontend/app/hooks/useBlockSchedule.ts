import { useState } from 'react';

import type { BlockSchedule } from '@/app/types/block-schedule';
import { api } from '@/lib/api';

import { useAuth } from '../../contexts/AuthContext';

export function useBlockSchedule() {
    const [schedules, setSchedules] = useState<BlockSchedule[]>([]);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const { user } = useAuth();

    const fetchSchedules = async () => {
        setLoading(true);
        try {
            const response = await api.get<BlockSchedule[]>('/api/schedules');
            setSchedules(response.data);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const createSchedule = async (data: Omit<BlockSchedule, 'id' | 'userId' | 'createdAt' | 'updatedAt'>) => {
        if (!user?.id) {
            throw new Error('User not authenticated');
        }

        try {
            const response = await api.post<BlockSchedule>('/api/schedules', {
                ...data,
                userId: user.id
            });
            setSchedules(prev => [...prev, response.data]);
            return response.data;
        } catch (err: any) {
            setError(err.message);
            throw err;
        }
    };

    const updateSchedule = async (id: string, data: Partial<BlockSchedule>) => {
        try {
            const response = await api.put<BlockSchedule>(`/api/schedules/${id}`, data);
            setSchedules(prev => prev.map(schedule =>
                schedule.id === id ? { ...schedule, ...response.data } : schedule
            ));
            return response.data;
        } catch (err: any) {
            setError(err.message);
            throw err;
        }
    };

    const deleteSchedule = async (id: string) => {
        try {
            await api.delete(`/api/schedules/${id}`);
            setSchedules(prev => prev.filter(schedule => schedule.id !== id));
        } catch (err: any) {
            setError(err.message);
            throw err;
        }
    };

    return {
        schedules,
        error,
        loading,
        fetchSchedules,
        createSchedule,
        updateSchedule,
        deleteSchedule
    };
}
