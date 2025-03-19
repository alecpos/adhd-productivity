import React from 'react';

import { makeStyles } from '@rneui/themed';
import { View } from 'react-native';

import { useTasks } from '../../../contexts/TaskContext';
import { TaskList } from '../TaskList';

interface TasksTabProps {
  onSubmit?: (text: string) => void;
}

export default function TasksTab({ onSubmit }: TasksTabProps) {
  const { tasks, loading, completeTask, deleteTask } = useTasks();
  const styles = useStyles();

  return (
    <View style={styles.container}>
      <TaskList 
        tasks={tasks}
        onCompleteTask={completeTask}
        onDeleteTask={deleteTask}
        loading={loading}
      />
    </View>
  );
}

const useStyles = makeStyles((theme) => ({
  container: {
    flex: 1,
    padding: theme.spacing.md,
  },
})); 