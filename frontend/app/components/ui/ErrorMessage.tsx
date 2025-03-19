import React from 'react';

import { Text, Icon } from '@rneui/themed';
import { View, StyleSheet } from 'react-native';

interface ErrorMessageProps {
  message: string;
}

export function ErrorMessage({ message }: ErrorMessageProps) {
  return (
    <View style={styles.container}>
      <Icon
        name="exclamation-circle"
        type="font-awesome-5"
        size={24}
        color="#dc3545"
        style={styles.icon}
      />
      <Text style={styles.message}>{message}</Text>
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
  icon: {
    marginBottom: 10,
  },
  message: {
    color: '#dc3545',
    fontSize: 16,
    textAlign: 'center',
  },
}); 