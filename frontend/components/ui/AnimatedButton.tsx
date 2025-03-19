import React, { useEffect } from 'react';

import { Button, useTheme } from '@rneui/themed';
import { TouchableOpacity, View } from 'react-native';
import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withSpring,
  withSequence,
  withDelay,
} from 'react-native-reanimated';

import type { ButtonProps} from '@rneui/themed';

interface AnimatedButtonProps extends Omit<ButtonProps, 'TouchableComponent'> {
  scaleOnPress?: boolean;
  pulseOnLoad?: boolean;
}

const AnimatedView = Animated.createAnimatedComponent(View);

export function AnimatedButton({
  onPress,
  scaleOnPress = false,
  pulseOnLoad = false,
  disabled = false,
  loading = false,
  containerStyle,
  ...props
}: AnimatedButtonProps) {
  const scale = useSharedValue(1);
  const { theme } = useTheme();

  useEffect(() => {
    if (pulseOnLoad) {
      scale.value = withSequence(
        withDelay(500, withSpring(1.1, { damping: 2 })),
        withSpring(1, { damping: 2 })
      );
    }
  }, [pulseOnLoad]);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  const handlePressIn = () => {
    if (scaleOnPress && !disabled && !loading) {
      scale.value = withSpring(0.95, { damping: 10 });
    }
  };

  const handlePressOut = () => {
    if (scaleOnPress && !disabled && !loading) {
      scale.value = withSpring(1, { damping: 10 });
    }
  };

  return (
    <AnimatedView style={[containerStyle, animatedStyle]}>
      <Button
        {...props}
        TouchableComponent={TouchableOpacity}
        onPress={onPress}
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
        disabled={disabled}
        loading={loading}
        containerStyle={{ margin: 0, padding: 0 }}
        buttonStyle={[
          {
            opacity: (disabled || loading) ? 0.5 : 1,
          },
          props.buttonStyle,
        ]}
      />
    </AnimatedView>
  );
} 