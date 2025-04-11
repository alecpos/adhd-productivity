import { useState, useCallback } from 'react';

import type { Task } from '@/app/types/task';
import { api } from '@/lib/api';

import { useAuth } from '../contexts/AuthContext';

export const useTaskSync = () => {
  const [syncing, setSyncing] = useState(false);
  const [lastSyncTime, setLastSyncTime] = useState<Date | null>(null);
  const { user } = useAuth();

  const syncTasks = useCallback(async () => {
    if (!user?.id) return;
    setSyncing(true);
    try {
      const response = await api.post<{ tasks: Task[] }>('/tasks/sync', {
        userId: user.id,
        lastSyncTime: lastSyncTime?.toISOString(),
      });
      setLastSyncTime(new Date());
      return response.data.tasks;
    } catch (error) {
      console.error('Error syncing tasks:', error);
      throw error;
    } finally {
      setSyncing(false);
    }
  }, [user?.id, lastSyncTime]);

  const forceSync = useCallback(async () => {
    setLastSyncTime(null);
    return syncTasks();
  }, [syncTasks]);

  return {
    syncing,
    lastSyncTime,
    syncTasks,
    forceSync,
  };
};
