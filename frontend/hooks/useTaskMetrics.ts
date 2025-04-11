import { useMemo } from 'react';

import type { Task} from '@/types/task';
import { TaskPriority } from '@/types/task';

export const useTaskMetrics = (tasks: Task[]) => {
  const metrics = useMemo(() => {
    const totalTasks = tasks.length;
    const completedTasks = tasks.filter(task => task.completed).length;
    const pendingTasks = totalTasks - completedTasks;
    const completionRate = totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0;

    const urgentTasks = tasks.filter(task => (task.urgency || 0) >= 8).length;
    const highImpactTasks = tasks.filter(task => (task.impact || 0) >= 8).length;

    const averageEffort = tasks.reduce((sum, task) => sum + (task.effort || 0), 0) / totalTasks || 0;

    const overdueTasks = tasks.filter(task => {
      if (!task.due_date) return false;
      const dueDate = new Date(task.due_date);
      return !task.completed && dueDate < new Date();
    }).length;

    const upcomingTasks = tasks.filter(task => {
      if (!task.due_date) return false;
      const dueDate = new Date(task.due_date);
      const today = new Date();
      const threeDaysFromNow = new Date(today.setDate(today.getDate() + 3));
      return !task.completed && dueDate <= threeDaysFromNow;
    }).length;

    return {
      totalTasks,
      completedTasks,
      pendingTasks,
      completionRate,
      urgentTasks,
      highImpactTasks,
      averageEffort,
      overdueTasks,
      upcomingTasks,
    };
  }, [tasks]);

  const getTaskEfficiencyScore = (task: Task) => {
    const impact = task.impact || 0;
    const urgency = task.urgency || 0;
    const effort = task.effort || 1;
    return ((impact * urgency) / effort) * 10;
  };

  const getTaskPriority = (task: Task) => {
    const score = getTaskEfficiencyScore(task);
    if (score >= 80) return TaskPriority.URGENT;
    if (score >= 60) return TaskPriority.HIGH;
    if (score >= 40) return TaskPriority.MEDIUM;
    return TaskPriority.LOW;
  };

  return {
    metrics,
    getTaskEfficiencyScore,
    getTaskPriority,
  };
};
