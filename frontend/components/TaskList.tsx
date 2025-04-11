import React, { useState, useMemo } from 'react';

import { makeStyles } from '@rneui/themed';
import { View, Text, FlatList } from 'react-native';

import { TaskCard } from '@/components/TaskCard';
import { useTasks } from '@/contexts/TaskContext';
import { Task, TaskPriority } from '@/types/task';

interface TaskListProps {
  filter?: string;
  sortField?: 'title' | 'due_date' | 'priority';
  sortDirection?: 'asc' | 'desc';
}

const useStyles = makeStyles((theme) => ({
    container: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    loadingText: {
        color: theme.colors.text,
    },
    errorText: {
        color: theme.colors.error,
    },
}));

export function TaskList({ filter = '', sortField = 'due_date', sortDirection = 'asc' }: TaskListProps) {
  const { tasks = [], loading, error, completeTask, deleteTask } = useTasks();
  const [selectedTask, setSelectedTask] = useState<string | null>(null);
  const styles = useStyles();

  const filteredAndSortedTasks = useMemo(() => {
    if (!Array.isArray(tasks)) return [];

    // Filter tasks
    const filteredTasks = tasks.filter(task => {
      // Handle special filter values
      if (filter === 'Completed') return task.completed;
      if (filter === 'Pending') return !task.completed;

      // Handle search text
      if (filter && typeof filter === 'string') {
        const searchLower = filter.toLowerCase();
        const titleMatch = task?.title?.toLowerCase().includes(searchLower) || false;
        const descriptionMatch = task?.description?.toLowerCase().includes(searchLower) || false;
        return titleMatch || descriptionMatch;
      }

      return true;
    });

    // Sort tasks
    return [...filteredTasks].sort((a, b) => {
      if (sortField === 'title') {
        return sortDirection === 'asc'
          ? (a.title || '').localeCompare(b.title || '')
          : (b.title || '').localeCompare(a.title || '');
      }

      if (sortField === 'due_date') {
        if (!a.due_date) return sortDirection === 'asc' ? 1 : -1;
        if (!b.due_date) return sortDirection === 'asc' ? -1 : 1;
        return sortDirection === 'asc'
          ? new Date(a.due_date).getTime() - new Date(b.due_date).getTime()
          : new Date(b.due_date).getTime() - new Date(a.due_date).getTime();
      }

      if (sortField === 'priority') {
        const priorityOrder: Record<TaskPriority, number> = {
          [TaskPriority.LOW]: 0,
          [TaskPriority.MEDIUM]: 1,
          [TaskPriority.HIGH]: 2,
          [TaskPriority.URGENT]: 3
        };
        const aPriority = priorityOrder[a.priority || TaskPriority.LOW];
        const bPriority = priorityOrder[b.priority || TaskPriority.LOW];
        return sortDirection === 'asc' ? aPriority - bPriority : bPriority - aPriority;
      }

      return 0;
    });
  }, [tasks, filter, sortField, sortDirection]);

  if (loading) {
    return (
      <View style={styles.container}>
        <Text style={styles.loadingText}>Loading tasks...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>Error: {error}</Text>
      </View>
    );
  }

  if (!Array.isArray(tasks) || !filteredAndSortedTasks.length) {
    return (
      <View style={styles.container}>
        <Text style={styles.loadingText}>No tasks found</Text>
      </View>
    );
  }

  return (
    <FlatList
      data={filteredAndSortedTasks}
      keyExtractor={(item) => item.id}
      renderItem={({ item }) => (
        <TaskCard
          task={item}
          onComplete={() => completeTask(item.id)}
          onDelete={() => deleteTask(item.id)}
        />
      )}
    />
  );
}
