import React, { useState } from 'react';

import axios from 'axios';
import { View, TextInput, Button, Alert } from 'react-native';

import { useAuth } from '../contexts/AuthContext';

export default function CreateTaskScreen({ navigation }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [dueDate, setDueDate] = useState('');
  const { user } = useAuth();

  const handleCreateTask = async () => {
    try {
      await axios.post('http://localhost:8000/tasks/', {
        title,
        description,
        due_date: dueDate,
        user_id: user.id,
      });
      Alert.alert('Task created successfully');
      navigation.goBack();
    } catch (error) {
      Alert.alert('Error', error.response.data.detail);
    }
  };

  return (
    <View>
      <TextInput
        placeholder="Title"
        value={title}
        onChangeText={setTitle}
        textContentType="none"
      />
      <TextInput
        placeholder="Description"
        value={description}
        onChangeText={setDescription}
        textContentType="none"
      />
      <TextInput
        placeholder="Due Date (YYYY-MM-DD)"
        value={dueDate}
        onChangeText={setDueDate}
        textContentType="none"
      />
      <Button title="Create Task" onPress={handleCreateTask} />
    </View>
  );
}
