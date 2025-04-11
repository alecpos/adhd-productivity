import React from 'react';

import { Text, Button, makeStyles, useTheme } from '@rneui/themed';
import { format } from 'date-fns';
import { View, TouchableOpacity } from 'react-native';

import { useHyperfocus } from 'contexts/HyperfocusContext';
import { useTasks } from 'contexts/TaskContext';

import type { Task } from 'app/types/task';


interface TaskCardProps {
  task: Task;
  onComplete?: () => void;
  onDelete?: () => void;
}

export function TaskCard({ task, onComplete, onDelete }: TaskCardProps) {
  const { completeTask, deleteTask } = useTasks();
  const { startSession } = useHyperfocus();
  const { theme } = useTheme();
  const styles = useStyles();

  const handleComplete = async () => {
    try {
      await completeTask(task.id);
      onComplete?.();
    } catch (error) {
      console.error('Error completing task:', error);
    }
  };

  const handleDelete = async () => {
    try {
      await deleteTask(task.id);
      onDelete?.();
    } catch (error) {
      console.error('Error deleting task:', error);
    }
  };

  const handleStartSession = async () => {
    try {
      await startSession({
        duration_minutes: task.estimated_duration || 25,
        task_id: task.id,
        purpose: `Focus session for: ${task.title}`
      });
    } catch (error) {
      console.error('Error starting focus session:', error);
    }
  };

  return (
    <TouchableOpacity style={[styles.container, task.completed && styles.completedContainer]}>
      <View style={styles.header}>
        <Text h4 style={[styles.title, task.completed && styles.completedText]}>
          {task.title}
        </Text>
        <Text style={styles.date}>
          {task.due_date ? format(new Date(task.due_date), 'MMM dd, yyyy') : 'No due date'}
        </Text>
      </View>

      {task.description && (
        <Text style={[styles.description, task.completed && styles.completedText]}>
          {task.description}
        </Text>
      )}

      <View style={styles.metrics}>
        <Text style={styles.metric}>Priority: {task.priority || 'Not set'}</Text>
        <Text style={styles.metric}>Energy: {task.energy_required || 'Not set'}</Text>
        {task.estimated_duration && (
          <Text style={styles.metric}>Duration: {task.estimated_duration}min</Text>
        )}
      </View>

      <View style={styles.buttonContainer}>
        <Button
          title={task.completed ? "Uncomplete" : "Complete"}
          onPress={handleComplete}
          type="outline"
          size="sm"
          containerStyle={styles.button}
        />
        <Button
          title="Focus"
          onPress={handleStartSession}
          type="solid"
          size="sm"
          containerStyle={styles.button}
        />
        <Button
          title="Delete"
          onPress={handleDelete}
          type="outline"
          size="sm"
          containerStyle={styles.button}
          buttonStyle={{ borderColor: theme.colors.error }}
          titleStyle={{ color: theme.colors.error }}
        />
      </View>
    </TouchableOpacity>
  );
}

const useStyles = makeStyles((theme) => ({
  container: {
    backgroundColor: theme.colors.background,
    borderRadius: theme.spacing.sm,
    padding: theme.spacing.md,
    marginBottom: theme.spacing.sm,
    borderWidth: 1,
    borderColor: theme.colors.grey4,
    ...theme.shadows.sm,
  },
  completedContainer: {
    backgroundColor: theme.colors.grey5,
    opacity: 0.8,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: theme.spacing.sm,
  },
  title: {
    color: theme.colors.primary,
    flex: 1,
    marginRight: theme.spacing.sm,
  },
  completedText: {
    textDecorationLine: 'line-through',
    color: theme.colors.grey2,
  },
  date: {
    fontSize: theme.fontSize.sm,
    color: theme.colors.grey3,
  },
  description: {
    fontSize: theme.fontSize.sm,
    color: theme.colors.grey1,
    marginBottom: theme.spacing.md,
  },
  metrics: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: theme.spacing.sm,
    marginBottom: theme.spacing.md,
  },
  metric: {
    fontSize: theme.fontSize.sm,
    color: theme.colors.grey2,
    backgroundColor: theme.colors.grey5,
    paddingHorizontal: theme.spacing.sm,
    paddingVertical: theme.spacing.xs,
    borderRadius: theme.spacing.xs,
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    gap: theme.spacing.sm,
  },
  button: {
    minWidth: 80,
  },
}));
