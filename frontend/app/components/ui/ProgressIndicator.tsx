import React from 'react';

import { Text, makeStyles, useTheme } from '@rneui/themed';
import { View, Animated } from 'react-native';

type ProgressVariant = 'linear' | 'circular';
type ProgressSize = 'small' | 'medium' | 'large';
type ProgressStatus = 'primary' | 'success' | 'warning' | 'error';

interface ProgressIndicatorProps {
  variant?: ProgressVariant;
  size?: ProgressSize;
  status?: ProgressStatus;
  progress?: number;
  showLabel?: boolean;
  label?: string;
  animated?: boolean;
}

export const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({
  variant = 'linear',
  size = 'medium',
  status = 'primary',
  progress = 0,
  showLabel = false,
  label,
  animated = true,
}) => {
  const styles = useStyles();
  const { theme } = useTheme();
  const animatedValue = React.useRef(new Animated.Value(0)).current;

  React.useEffect(() => {
    if (animated) {
      Animated.timing(animatedValue, {
        toValue: progress,
        duration: 1000,
        useNativeDriver: false,
      }).start();
    } else {
      animatedValue.setValue(progress);
    }
  }, [progress, animated]);

  const getStatusColor = () => {
    const colors = {
      primary: theme.colors.primary,
      success: theme.colors.success,
      warning: theme.colors.warning,
      error: theme.colors.error,
    };
    return colors[status];
  };

  const getSizeStyles = () => {
    const sizes = {
      small: styles.smallProgress,
      medium: styles.mediumProgress,
      large: styles.largeProgress,
    };
    return sizes[size];
  };

  const renderLinearProgress = () => {
    const width = animatedValue.interpolate({
      inputRange: [0, 1],
      outputRange: ['0%', '100%'],
    });

    return (
      <View style={[styles.linearContainer, getSizeStyles()]}>
        <Animated.View
          style={[
            styles.linearProgress,
            { backgroundColor: getStatusColor(), width },
          ]}
        />
      </View>
    );
  };

  const renderCircularProgress = () => {
    // Note: For a more sophisticated circular progress,
    // consider using react-native-svg or similar libraries
    return (
      <View style={[styles.circularContainer, getSizeStyles()]}>
        <View
          style={[
            styles.circularProgress,
            { borderColor: getStatusColor() },
          ]}
        />
      </View>
    );
  };

  return (
    <View style={styles.container}>
      {variant === 'linear' ? renderLinearProgress() : renderCircularProgress()}
      {showLabel && (
        <Text style={styles.label}>
          {label || `${Math.round(progress * 100)}%`}
        </Text>
      )}
    </View>
  );
};

const useStyles = makeStyles((theme) => ({
  container: {
    marginVertical: theme.spacing.sm,
  },
  linearContainer: {
    backgroundColor: theme.colors.grey5,
    borderRadius: theme.borderRadius.sm,
    overflow: 'hidden',
  },
  linearProgress: {
    height: '100%',
    borderRadius: theme.borderRadius.sm,
  },
  circularContainer: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  circularProgress: {
    borderWidth: 4,
    borderRadius: 100,
    borderStyle: 'solid',
  },
  label: {
    marginTop: theme.spacing.xs,
    fontSize: theme.fontSize.sm,
    color: theme.colors.grey1,
    textAlign: 'center',
  },
  // Size variants
  smallProgress: {
    height: 4,
  },
  mediumProgress: {
    height: 8,
  },
  largeProgress: {
    height: 12,
  },
})); 