import { useState, useCallback } from 'react';

import { api } from '../services/api';
import type { Task, TaskStatus } from '../types/task';

interface TaskStateHook {
  currentTask: Task;
  isUpdating: boolean;
  error: string | null;
  updateTaskStatus: (newStatus: TaskStatus) => Promise<boolean>;
  getNextStates: () => TaskStatus[];
  canTransitionTo: (status: TaskStatus) => boolean;
}

export const useTaskState = (task: Task): TaskStateHook => {
  const [currentTask, setCurrentTask] = useState<Task>(task);
  const [isUpdating, setIsUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updateTaskStatus = useCallback(async (newStatus: TaskStatus): Promise<boolean> => {
    if (!currentTask.next_states.includes(newStatus)) {
      setError(`Invalid state transition from ${currentTask.status} to ${newStatus}`);
      return false;
    }

    setIsUpdating(true);
    setError(null);

    try {
      const response = await api.patch(`/tasks/${currentTask.id}/status`, {
        status: newStatus
      });
      
      setCurrentTask(response.data);
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update task status');
      return false;
    } finally {
      setIsUpdating(false);
    }
  }, [currentTask]);

  const getNextStates = useCallback((): TaskStatus[] => {
    return currentTask.next_states;
  }, [currentTask]);

  const canTransitionTo = useCallback((status: TaskStatus): boolean => {
    return currentTask.next_states.includes(status);
  }, [currentTask]);

  return {
    currentTask,
    isUpdating,
    error,
    updateTaskStatus,
    getNextStates,
    canTransitionTo
  };
}; 