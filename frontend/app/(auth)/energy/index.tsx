import React, { useState } from "react";

import { Text, Slider, Input, Button, makeStyles, useTheme } from "@rneui/themed";
import { View, Alert } from "react-native";

import { api } from "@/lib/api";

import { useAuth } from "../../../contexts/AuthContext";


export default function EnergyMappingScreen() {
  const [energyLevel, setEnergyLevel] = useState(5);
  const [notes, setNotes] = useState("");
  const { user } = useAuth();
  const styles = useStyles();
  const { theme } = useTheme();

  const handleLogEnergy = async () => {
    if (!user) {
      Alert.alert("Error", "User not authenticated. Please log in.");
      return;
    }

    try {
      await api.post("/api/energy-mapping/log", {
        user_id: user.id,
        energy_level: energyLevel,
        notes,
      });
      Alert.alert("Success", "Energy level logged successfully!");
      setNotes("");
      setEnergyLevel(5);
    } catch (error: any) {
      Alert.alert("Error", error.response?.data?.detail || "Error logging energy level");
    }
  };

  return (
    <View style={styles.container}>
      <Text h4>Energy Level: {energyLevel}</Text>
      <Slider
        value={energyLevel}
        onValueChange={(value) => setEnergyLevel(value)}
        maximumValue={10}
        minimumValue={1}
        step={1}
        style={styles.slider}
        thumbStyle={styles.thumb}
        trackStyle={styles.track}
      />
      <Input
        placeholder="Add notes..."
        value={notes}
        onChangeText={setNotes}
        containerStyle={styles.input}
      />
      <Button title="Log Energy" onPress={handleLogEnergy} />
    </View>
  );
}

const useStyles = makeStyles((theme) => ({
  container: { 
    padding: theme.spacing.lg 
  },
  slider: { 
    marginVertical: theme.spacing.lg 
  },
  thumb: { 
    height: 20, 
    width: 20,
    backgroundColor: theme.colors.primary 
  },
  track: { 
    height: 5,
    backgroundColor: theme.colors.grey5 
  },
  input: { 
    marginBottom: theme.spacing.lg 
  },
}));
