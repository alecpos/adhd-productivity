import React from 'react';

import { Text, makeStyles, useTheme } from '@rneui/themed';
import { View, ActivityIndicator, Modal } from 'react-native';

interface LoadingOverlayProps {
  visible: boolean;
  message?: string;
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  visible,
  message = 'Loading...',
}) => {
  const styles = useStyles();
  const { theme } = useTheme();

  return (
    <Modal
      transparent
      animationType="fade"
      visible={visible}
    >
      <View style={styles.container}>
        <View style={styles.content}>
          <ActivityIndicator 
            size="large" 
            color={theme.colors.primary} 
          />
          {message && (
            <Text style={styles.message}>{message}</Text>
          )}
        </View>
      </View>
    </Modal>
  );
};

const useStyles = makeStyles((theme) => ({
  container: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.4)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {
    backgroundColor: theme.colors.background,
    padding: theme.spacing.lg,
    borderRadius: theme.borderRadius.md,
    alignItems: 'center',
    ...theme.shadows.md,
  },
  message: {
    marginTop: theme.spacing.md,
    fontSize: theme.fontSize.sm,
    color: theme.colors.grey1,
  },
})); 