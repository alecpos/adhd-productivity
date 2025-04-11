import { useState, useCallback, useEffect } from 'react';

import { useADHDSettings } from '../contexts/ADHDSettingsContext';
import { useTasks } from '../contexts/TaskContext';
import { TaskStatus, TaskPriority } from '../types/task';

import type { Task} from '../types/task';

interface TaskBreakdown {
  steps: string[];
  estimatedDuration: number;
  complexity: number;
  prerequisites: string[];
  potentialObstacles: string[];
  adaptations: {
    visualAids: boolean;
    timeboxed: boolean;
    externalAccountability: boolean;
    environmentalModifications: string[];
  };
}

interface TaskMetrics {
  completionRate: number;
  averageTimeToStart: number;
  averageDurationAccuracy: number;
  commonObstacles: { obstacle: string; frequency: number }[];
  successfulStrategies: { strategy: string; effectiveness: number }[];
  environmentalFactors: { factor: string; impact: number }[];
}

interface TaskAdaptation {
  visualAids: boolean;
  timeboxed: boolean;
  externalAccountability: boolean;
  breakdownNeeded: boolean;
  environmentalModifications: string[];
  reminders: {
    type: string;
    frequency: number;
    message: string;
  }[];
  supportStrategies: {
    type: string;
    description: string;
    trigger: string;
  }[];
}

interface ExtendedTask extends Task {
  adhd_metrics?: TaskMetrics;
  adaptations?: TaskAdaptation;
}

export const useADHDTaskManagement = () => {
  const { profile, metrics, logExecutiveFunction } = useADHDSettings();
  const { tasks, updateTask, fetchTasks } = useTasks();
  const [taskMetrics, setTaskMetrics] = useState<Record<string, TaskMetrics>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const breakdownTask = useCallback(async (task: Task): Promise<TaskBreakdown> => {
    // Implementation details...
    return {
      steps: [],
      estimatedDuration: task.estimated_duration || 0,
      complexity: task.effort || 1,
      prerequisites: [],
      potentialObstacles: [],
      adaptations: {
        visualAids: false,
        timeboxed: false,
        externalAccountability: false,
        environmentalModifications: []
      }
    };
  }, []);

  const updateTaskWithADHDMetrics = useCallback(async (taskId: string, metrics: TaskMetrics) => {
    try {
      const taskToUpdate = tasks.find(t => t.id === taskId);
      if (!taskToUpdate) return;

      const extendedTask: ExtendedTask = {
        ...taskToUpdate,
        adhd_metrics: metrics
      };

      await updateTask(taskId, {
        description: JSON.stringify({
          ...JSON.parse(taskToUpdate.description || '{}'),
          adhd_metrics: metrics
        })
      });

      setTaskMetrics(prev => ({
        ...prev,
        [taskId]: metrics
      }));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update task metrics');
    }
  }, [tasks, updateTask]);

  // ... rest of the implementation

  return {
    taskMetrics,
    loading,
    error,
    breakdownTask,
    updateTaskWithADHDMetrics
  };
};
