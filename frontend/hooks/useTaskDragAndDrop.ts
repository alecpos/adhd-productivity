import { useState, useCallback } from 'react';

import type { Task } from '@/app/types/task';

export const useTaskDragAndDrop = (tasks: Task[], onReorder: (tasks: Task[]) => void) => {
  const [draggingTask, setDraggingTask] = useState<Task | null>(null);

  const handleDragStart = useCallback((task: Task) => {
    setDraggingTask(task);
  }, []);

  const handleDragEnd = useCallback(() => {
    setDraggingTask(null);
  }, []);

  const handleDragOver = useCallback((task: Task) => {
    if (!draggingTask || task.id === draggingTask.id) return;

    const updatedTasks = [...tasks];
    const draggedIndex = tasks.findIndex(t => t.id === draggingTask.id);
    const dropIndex = tasks.findIndex(t => t.id === task.id);

    updatedTasks.splice(draggedIndex, 1);
    updatedTasks.splice(dropIndex, 0, draggingTask);

    onReorder(updatedTasks);
  }, [draggingTask, tasks, onReorder]);

  return {
    draggingTask,
    handleDragStart,
    handleDragEnd,
    handleDragOver,
  };
};
