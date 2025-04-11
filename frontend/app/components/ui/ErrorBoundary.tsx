import React from 'react';

import { Text, Button } from '@rneui/themed';
import { View, StyleSheet } from 'react-native';

interface Props {
  error: Error;
  onRetry?: () => void;
  children?: React.ReactNode;
}

export function ErrorBoundary({ error, onRetry, children }: Props) {
  if (error) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>Something went wrong</Text>
        <Text style={styles.errorDetail}>{error.message}</Text>
        {onRetry && (
          <Button
            title="Try Again"
            onPress={onRetry}
            type="outline"
            containerStyle={styles.buttonContainer}
          />
        )}
      </View>
    );
  }

  return <>{children}</>;
}

export const ErrorDisplay = ({ error }: { error: string }) => {
  return (
    <View style={styles.errorContainer}>
      <Text style={styles.errorText}>{error}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  errorText: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  errorDetail: {
    color: '#666',
    textAlign: 'center',
    marginBottom: 20,
  },
  buttonContainer: {
    marginTop: 10,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
});
