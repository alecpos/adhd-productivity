import React from 'react';

import { View, ActivityIndicator, StyleSheet, Text } from 'react-native';

interface Props {
  message?: string;
}

export function LoadingSpinner({ message = 'Loading...' }: Props) {
  return (
    <View style={styles.container}>
      <ActivityIndicator size="large" color="#0000ff" />
      <Text style={styles.text}>{message}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  text: {
    marginTop: 10,
    color: '#666',
  },
});
