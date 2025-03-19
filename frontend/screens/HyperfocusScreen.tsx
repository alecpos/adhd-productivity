import React, { useState } from 'react';

import axios from 'axios';
import { View, Button, Text, Alert } from 'react-native';

import { useAuth } from '../contexts/AuthContext';

export default function HyperfocusScreen() {
  const [session, setSession] = useState(null);
  const { user } = useAuth();

  const startSession = async () => {
    try {
      const response = await axios.post('http://localhost:8000/hyperfocus/start', {
        user_id: user.id,
        duration_minutes: 60, // Or prompt user for duration
      });
      setSession(response.data.data);
      Alert.alert('Hyperfocus session started');
    } catch (error) {
      Alert.alert('Error', error.response.data.detail);
    }
  };

  const endSession = async () => {
    try {
      await axios.post('http://localhost:8000/hyperfocus/end', {
        user_id: user.id,
      });
      setSession(null);
      Alert.alert('Hyperfocus session ended');
    } catch (error) {
      Alert.alert('Error', error.response.data.detail);
    }
  };

  return (
    <View>
      {session ? (
        <View>
          <Text>Session Active</Text>
          <Button title="End Session" onPress={endSession} />
        </View>
      ) : (
        <Button title="Start Hyperfocus Session" onPress={startSession} />
      )}
    </View>
  );
}
