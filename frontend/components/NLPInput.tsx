import React, { useState } from "react";

import { TextInput, Button, View, StyleSheet } from "react-native";

import { useTasks } from "../contexts/TaskContext";

const NLPInput = ({ userId }: { userId: string }) => {
  const { processNLPInput } = useTasks();
  const [inputText, setInputText] = useState("");

  const handleProcess = () => {
    if (inputText.trim()) {
      processNLPInput(inputText, userId);
      setInputText(""); // Clear input after processing
    }
  };

  return (
    <View style={styles.container}>
      <TextInput
        style={styles.input}
        placeholder="Describe your task..."
        value={inputText}
        onChangeText={setInputText}
      />
      <Button title="Add Task" onPress={handleProcess} />
    </View>
  );
};

const styles = StyleSheet.create({
  container: { padding: 16 },
  input: { borderWidth: 1, padding: 8, marginBottom: 8, borderRadius: 4 },
});

export default NLPInput;
