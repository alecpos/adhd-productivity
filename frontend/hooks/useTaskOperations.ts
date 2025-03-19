import { useState, useCallback } from 'react';

import { useAuth } from '../contexts/AuthContext';
import { taskService } from '../core/api/services/taskService';

import type { Task, CreateTaskRequest } from '../core/api/services/taskService';

interface UseTaskOperationsResult {
  tasks: Task[];
  loading: boolean;
  error: string | null;
  fetchTasks: () => Promise<void>;
  createTask: (taskData: Omit<CreateTaskRequest, "user_id">) => Promise<void>;
  updateTask: (taskId: string, taskData: Partial<Task>) => Promise<void>;
  deleteTask: (taskId: string) => Promise<void>;
  completeTask: (taskId: string, completionNotes?: string) => Promise<void>;
}

export function useTaskOperations(): UseTaskOperationsResult {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();

  const fetchTasks = useCallback(async (): Promise<void> => {
    if (user?.id === undefined) {
      return;
    }
    
    setLoading(true);
    setError(null);
    try {
      const fetchedTasks = await taskService.getUserTasks(user.id);
      setTasks(fetchedTasks);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch tasks';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [user?.id]);

  const createTask = useCallback(async (taskData: Omit<CreateTaskRequest, "user_id">): Promise<void> => {
    if (user?.id === undefined) {
      throw new Error('User not authenticated');
    }
    
    setLoading(true);
    setError(null);
    try {
      const newTask = await taskService.createTask({
        ...taskData,
        user_id: user.id
      });
      setTasks(prev => [...prev, newTask]);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create task';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [user?.id]);

  const updateTask = useCallback(async (taskId: string, taskData: Partial<Task>): Promise<void> => {
    setLoading(true);
    setError(null);
    try {
      const updatedTask = await taskService.updateTask(taskId, taskData);
      setTasks(prev => prev.map(task => 
        task.id === taskId ? updatedTask : task
      ));
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update task';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteTask = useCallback(async (taskId: string): Promise<void> => {
    setLoading(true);
    setError(null);
    try {
      await taskService.deleteTask(taskId);
      setTasks(prev => prev.filter(task => task.id !== taskId));
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete task';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  const completeTask = useCallback(async (taskId: string, completionNotes?: string): Promise<void> => {
    setLoading(true);
    setError(null);
    try {
      const completedTask = await taskService.completeTask(taskId, completionNotes);
      setTasks(prev => prev.map(task => 
        task.id === taskId ? completedTask : task
      ));
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to complete task';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    tasks,
    loading,
    error,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    completeTask,
  };
} 