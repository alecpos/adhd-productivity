import React, { useState } from "react";

import { View, Text, TextInput, Button, StyleSheet, Alert } from "react-native";
import { ProgressBar } from "react-native-paper";

import { useHyperfocus } from "../contexts/HyperfocusContext";

const HyperfocusMode = () => {
  const { hyperfocus, startSession, endSession, logInterruption } = useHyperfocus();
  const [interruptionReason, setInterruptionReason] = useState("");

  const handleStartSession = () => {
    startSession(60).then(() => Alert.alert("Session Started"));
  };

  const handleEndSession = () => {
    endSession().then(() => Alert.alert("Session Ended"));
  };

  const handleLogInterruption = () => {
    if (!interruptionReason.trim()) {
      Alert.alert("Validation Error", "Please provide a reason.");
      return;
    }
    logInterruption(interruptionReason).then(() => {
      Alert.alert("Interruption Logged");
      setInterruptionReason("");
    });
  };

  return (
    <View style={styles.container}>
      {hyperfocus.sessionActive ? (
        <>
          <Text style={styles.heading}>Hyperfocus Session Active</Text>
          <ProgressBar progress={hyperfocus.remainingTime / 60} style={styles.progressBar} />
          <Text>{hyperfocus.remainingTime} minutes remaining</Text>
          <TextInput
            style={styles.input}
            placeholder="Reason for Interruption"
            value={interruptionReason}
            onChangeText={setInterruptionReason}
          />
          <Button title="Log Interruption" onPress={handleLogInterruption} />
          <Button title="End Session" onPress={handleEndSession} />
        </>
      ) : (
        <Button title="Start Session" onPress={handleStartSession} />
      )}
      <Text style={styles.streakText}>Streak: {hyperfocus.streaks.current_streak} days</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { padding: 20 },
  heading: { fontSize: 20, fontWeight: "bold", marginBottom: 10 },
  progressBar: { marginVertical: 10 },
  input: { borderWidth: 1, padding: 8, marginBottom: 8, borderRadius: 4 },
  streakText: { marginTop: 10, fontStyle: "italic" },
});

export default HyperfocusMode;
