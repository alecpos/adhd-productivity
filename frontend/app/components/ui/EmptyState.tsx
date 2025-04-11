import React from 'react';

import { Text, Icon, Button, makeStyles, useTheme } from '@rneui/themed';
import { View } from 'react-native';

interface EmptyStateProps {
  title: string;
  message: string;
  icon?: string;
  action?: {
    label: string;
    onPress: () => void;
  };
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  message,
  icon = 'inbox',
  action,
}) => {
  const styles = useStyles();

  return (
    <View style={styles.container}>
      <Icon
        name={icon}
        type="material"
        size={64}
        color={styles.icon.color}
      />
      <Text style={styles.title}>{title}</Text>
      <Text style={styles.message}>{message}</Text>
      {action && (
        <Button
          onPress={action.onPress}
          style={styles.button}
        >
          {action.label}
        </Button>
      )}
    </View>
  );
};

const useStyles = makeStyles((theme) => ({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: theme.spacing.xl,
  },
  icon: {
    color: theme.colors.grey3,
    marginBottom: theme.spacing.lg,
  },
  title: {
    fontSize: theme.fontSize.lg,
    fontWeight: 'bold',
    marginBottom: theme.spacing.sm,
    textAlign: 'center',
  },
  message: {
    fontSize: theme.fontSize.md,
    color: theme.colors.grey2,
    textAlign: 'center',
    marginBottom: theme.spacing.lg,
  },
  button: {
    marginTop: theme.spacing.md,
  },
}));
