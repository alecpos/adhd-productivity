import React, { useState } from 'react';

import axios from 'axios';
import { View, Slider, TextInput, Button, Alert } from 'react-native';

import { useAuth } from '../contexts/AuthContext';

export default function EnergyMappingScreen() {
  const [energyLevel, setEnergyLevel] = useState(5);
  const [notes, setNotes] = useState('');
  const { user } = useAuth();

  const handleLogEnergy = async () => {
    try {
      await axios.post('http://localhost:8000/energy-mapping/log', {
        user_id: user.id,
        energy_level: energyLevel,
        notes,
      });
      Alert.alert('Energy level logged successfully');
    } catch (error) {
      Alert.alert('Error', error.response.data.detail);
    }
  };

  return (
    <View>
      <Slider
        minimumValue={1}
        maximumValue={10}
        step={1}
        value={energyLevel}
        onValueChange={setEnergyLevel}
      />
      <TextInput
        placeholder="Notes"
        value={notes}
        onChangeText={setNotes}
        textContentType="none"
      />
      <Button title="Log Energy" onPress={handleLogEnergy} />
    </View>
  );
}
