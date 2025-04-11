import React, { useState, useEffect } from "react";

import axios from "axios";
import { useRouter, useLocalSearchParams } from "expo-router";
import { View, TextInput, Button, Alert, StyleSheet, ActivityIndicator } from "react-native";

import { useAuth } from "../../../contexts/AuthContext";

export default function EditTaskScreen() {
  const [task, setTask] = useState<any>(null);
  const { user } = useAuth();
  const router = useRouter();
  const { id } = useLocalSearchParams();

  useEffect(() => {
    if (!user) {
      Alert.alert("Error", "User is not logged in.");
      router.replace("/(unauth)/login");
      return;
    }
  }, [user]);

  useEffect(() => {
    const fetchTask = async () => {
      if (!id || !user) return; // Avoid fetching if prerequisites aren't met
      try {
        const response = await axios.get(`http://localhost:8000/tasks/${id}`);
        setTask(response.data);
      } catch (error) {
        console.error("Failed to fetch task:", error);
      }
    };
    fetchTask();
  }, [id, user]);

  const handleUpdateTask = async () => {
    if (!user) {
      Alert.alert("Error", "User is not logged in.");
      return;
    }

    try {
      await axios.put(`http://localhost:8000/tasks/${id}`, {
        ...task,
        user_id: user.id,
      });
      Alert.alert("Task updated successfully");
      router.back();
    } catch (error: any) {
      Alert.alert("Error", error.response?.data?.detail || "Error");
    }
  };


  if (!task || !user) return <ActivityIndicator size="large" color="#0000ff" />;

  return (
    <View style={styles.container}>
      <TextInput
        placeholder="Title"
        value={task.title}
        onChangeText={(text) => setTask({ ...task, title: text })}
        style={styles.input}
      />
      <TextInput
        placeholder="Description"
        value={task.description}
        onChangeText={(text) => setTask({ ...task, description: text })}
        style={styles.input}
      />
      <TextInput
        placeholder="Due Date (YYYY-MM-DD)"
        value={task.due_date}
        onChangeText={(text) => setTask({ ...task, due_date: text })}
        style={styles.input}
      />
      <Button title="Update Task" onPress={handleUpdateTask} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 20,
  },
  input: {
    marginBottom: 10,
  },
});
