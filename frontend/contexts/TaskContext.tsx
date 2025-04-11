import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';

import { AxiosError } from 'axios';
import { Alert } from 'react-native';

import { taskService } from '../core/api/services/taskService';

import { useAuth } from './AuthContext';

import type { Task, CreateTaskRequest, TaskStatistics} from '../core/api/services/taskService';





interface TaskContextType {
  tasks: Task[];
  loading: boolean;
  error: string | null;
  statistics: TaskStatistics | null;
  fetchTasks: () => Promise<void>;
  createTask: (taskData: Omit<CreateTaskRequest, "user_id">) => Promise<void>;
  updateTask: (taskId: string, taskData: Partial<Task>) => Promise<void>;
  deleteTask: (taskId: string) => Promise<void>;
  completeTask: (taskId: string, completionNotes?: string) => Promise<void>;
  getTaskStats: () => Promise<void>;
}

const TaskContext = createContext<TaskContextType | undefined>(undefined);

export function TaskProvider({ children }: { children: React.ReactNode }) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statistics, setStatistics] = useState<TaskStatistics | null>(null);
  const { user, isAuthenticated, isInitialized } = useAuth();

  const handleError = (err: unknown, defaultMessage: string) => {
    let errorMessage = defaultMessage;

    if (err instanceof Error) {
      errorMessage = err.message;
    } else if (err instanceof AxiosError && err.response?.data) {
      const responseData = err.response.data as { detail?: string };
      if (responseData.detail) {
        errorMessage = responseData.detail;
      }
    }

    setError(errorMessage);
    Alert.alert('Error', errorMessage);
    throw err;
  };

  const fetchTasks = useCallback(async () => {
    if (!isAuthenticated || !user?.id) return;

    setLoading(true);
    setError(null);
    try {
      const fetchedTasks = await taskService.getUserTasks(user.id);
      setTasks(fetchedTasks);
    } catch (err) {
      handleError(err, 'Failed to fetch tasks');
    } finally {
      setLoading(false);
    }
  }, [user?.id, isAuthenticated]);

  const createTask = async (taskData: Omit<CreateTaskRequest, "user_id">) => {
    if (!isAuthenticated || !user?.id) {
      const message = 'User not authenticated';
      setError(message);
      Alert.alert('Error', message);
      throw new Error(message);
    }

    setLoading(true);
    setError(null);
    try {
      const newTask = await taskService.createTask({
        ...taskData,
        user_id: user.id
      });
      setTasks(prev => [...prev, newTask]);
      Alert.alert('Success', 'Task created successfully');
    } catch (err) {
      handleError(err, 'Failed to create task');
    } finally {
      setLoading(false);
    }
  };

  const updateTask = async (taskId: string, taskData: Partial<Task>) => {
    if (!isAuthenticated) return;

    setLoading(true);
    setError(null);
    try {
      const updatedTask = await taskService.updateTask(taskId, taskData);
      setTasks(prev => prev.map(task =>
        task.id === taskId ? updatedTask : task
      ));
      Alert.alert('Success', 'Task updated successfully');
    } catch (err) {
      handleError(err, 'Failed to update task');
    } finally {
      setLoading(false);
    }
  };

  const deleteTask = async (taskId: string) => {
    if (!isAuthenticated) return;

    setLoading(true);
    setError(null);
    try {
      await taskService.deleteTask(taskId);
      setTasks(prev => prev.filter(task => task.id !== taskId));
      Alert.alert('Success', 'Task deleted successfully');
    } catch (err) {
      handleError(err, 'Failed to delete task');
    } finally {
      setLoading(false);
    }
  };

  const completeTask = async (taskId: string, completionNotes?: string) => {
    if (!isAuthenticated) return;

    setLoading(true);
    setError(null);
    try {
      const completedTask = await taskService.completeTask(taskId, completionNotes);
      setTasks(prev => prev.map(task =>
        task.id === taskId ? completedTask : task
      ));
      await getTaskStats(); // Refresh statistics after completing a task
      Alert.alert('Success', 'Task completed successfully');
    } catch (err) {
      handleError(err, 'Failed to complete task');
    } finally {
      setLoading(false);
    }
  };

  const getTaskStats = async () => {
    if (!isAuthenticated || !user?.id) return;

    try {
      const stats = await taskService.getTaskStatistics();
      setStatistics(stats);
    } catch (err) {
      handleError(err, 'Failed to fetch task statistics');
    }
  };

  // Fetch tasks and statistics when the user changes and auth is initialized
  useEffect(() => {
    if (isInitialized && isAuthenticated) {
      fetchTasks();
      getTaskStats();
    } else {
      setTasks([]);
      setStatistics(null);
    }
  }, [isInitialized, isAuthenticated, fetchTasks]);

  return (
    <TaskContext.Provider
      value={{
        tasks,
        loading,
        error,
        statistics,
        fetchTasks,
        createTask,
        updateTask,
        deleteTask,
        completeTask,
        getTaskStats,
      }}
    >
      {children}
    </TaskContext.Provider>
  );
}

export function useTasks() {
  const context = useContext(TaskContext);
  if (!context) {
    throw new Error('useTasks must be used within a TaskProvider');
  }
  return context;
}
