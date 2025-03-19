// app/(auth)/tasks/index.tsx
import React, { useEffect, useState } from "react";

import { Button, Text, Badge } from "@rneui/themed";
import { View, StyleSheet, FlatList, RefreshControl } from "react-native";

import { ErrorBoundary } from "../../../app/components/ui/ErrorBoundary";
import { LoadingSpinner } from "../../../components/Loading/LoadingSpinner";
import { TaskCard } from "../../../components/TaskCard";
import { useAuth } from "../../../contexts/AuthContext";
import { useTasks } from "../../../contexts/TaskContext";

export default function TasksScreen() {
  const { user } = useAuth();
  const { tasks, fetchTasks, loading, completeTask, deleteTask, error } = useTasks();
  const [filter, setFilter] = useState<"All" | "Completed" | "Pending">("All");
  const [refreshing, setRefreshing] = useState(false);

  const onRefresh = React.useCallback(async () => {
    setRefreshing(true);
    try {
      await fetchTasks();
    } catch (error) {
      console.error("Failed to refresh tasks:", error);
    } finally {
      setRefreshing(false);
    }
  }, [fetchTasks]);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const handleComplete = async (taskId: string) => {
    try {
      await completeTask(taskId);
    } catch (error) {
      console.error("Failed to complete task:", error);
    }
  };

  if (error) {
    return (
      <ErrorBoundary 
        error={new Error(error)} 
        onRetry={fetchTasks} 
      />
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={tasks}
        renderItem={({ item }) => (
          <TaskCard 
            task={{
              id: item.id,
              title: item.title || '',
              description: item.description || '',
              due_date: item.due_date || '',
              urgency: item.urgency || 0,
              impact: item.impact || 0,
              effort: item.effort || 0,
              completed: item.completed || false,
              user_id: item.user_id || '',
              created_at: item.created_at || new Date().toISOString(),
              updated_at: item.updated_at || new Date().toISOString(),
              priority: item.priority || 'medium',
              status: item.status || 'pending'
            }}
            onComplete={() => handleComplete(item.id)}
            onDelete={() => deleteTask(item.id)}
          />
        )}
        keyExtractor={item => item.id}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          loading ? (
            <LoadingSpinner />
          ) : (
            <Text style={styles.emptyText}>No tasks found</Text>
          )
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  emptyText: {
    textAlign: 'center',
    marginTop: 20,
    color: '#666',
  }
});
