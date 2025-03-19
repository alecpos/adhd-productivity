import React from 'react';

import { makeStyles, useTheme, Icon, Text } from '@rneui/themed';
import { View, Animated, TouchableOpacity } from 'react-native';

type ToastType = 'success' | 'error' | 'warning' | 'info';
type ToastPosition = 'top' | 'bottom';

interface ToastProps {
  visible: boolean;
  type?: ToastType;
  message: string;
  position?: ToastPosition;
  duration?: number;
  onClose?: () => void;
  action?: {
    label: string;
    onPress: () => void;
  };
}

export const Toast: React.FC<ToastProps> = ({
  visible,
  type = 'info',
  message,
  position = 'bottom',
  duration = 3000,
  onClose,
  action,
}) => {
  const { theme } = useTheme();
  const styles = useStyles();
  const fadeAnim = React.useRef(new Animated.Value(0)).current;
  const translateY = React.useRef(new Animated.Value(position === 'top' ? -100 : 100)).current;

  React.useEffect(() => {
    if (visible) {
      Animated.parallel([
        Animated.timing(fadeAnim, {
          toValue: 1,
          duration: 200,
          useNativeDriver: true,
        }),
        Animated.timing(translateY, {
          toValue: 0,
          duration: 200,
          useNativeDriver: true,
        }),
      ]).start();

      if (duration !== 0) {
        const timer = setTimeout(() => {
          handleClose();
        }, duration);

        return () => clearTimeout(timer);
      }
    }
  }, [visible]);

  const handleClose = () => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 0,
        duration: 200,
        useNativeDriver: true,
      }),
      Animated.timing(translateY, {
        toValue: position === 'top' ? -100 : 100,
        duration: 200,
        useNativeDriver: true,
      }),
    ]).start(() => {
      onClose?.();
    });
  };

  const getTypeStyles = () => {
    const types = {
      success: {
        backgroundColor: theme.colors.success,
        icon: 'check-circle',
      },
      error: {
        backgroundColor: theme.colors.error,
        icon: 'error',
      },
      warning: {
        backgroundColor: theme.colors.warning,
        icon: 'warning',
      },
      info: {
        backgroundColor: theme.colors.primary,
        icon: 'info',
      },
    };
    return types[type];
  };

  if (!visible) return null;

  return (
    <Animated.View
      style={[
        styles.container,
        {
          [position]: 16,
          opacity: fadeAnim,
          transform: [{ translateY }],
          backgroundColor: getTypeStyles().backgroundColor,
        },
      ]}
    >
      <View style={styles.content}>
        <Icon
          name={getTypeStyles().icon}
          color="white"
          size={24}
          style={styles.icon}
        />
        <Text style={styles.message}>{message}</Text>
      </View>
      <View style={styles.actions}>
        {action && (
          <TouchableOpacity onPress={action.onPress}>
            <Text style={styles.actionText}>{action.label}</Text>
          </TouchableOpacity>
        )}
        {onClose && (
          <TouchableOpacity onPress={handleClose}>
            <Icon name="close" color="white" size={24} />
          </TouchableOpacity>
        )}
      </View>
    </Animated.View>
  );
};

const useStyles = makeStyles((theme) => ({
  container: {
    position: 'absolute',
    left: 16,
    right: 16,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    borderRadius: 8,
    shadowColor: theme.colors.black,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 4,
    elevation: 5,
  },
  content: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
  },
  icon: {
    marginRight: 12,
  },
  message: {
    color: theme.colors.white,
    fontSize: 14,
    flex: 1,
  },
  actions: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  actionText: {
    color: theme.colors.white,
    fontSize: 14,
    fontWeight: 'bold',
    marginRight: 16,
    textTransform: 'uppercase',
  },
}));

export default Toast; 