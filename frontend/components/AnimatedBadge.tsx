import React from 'react';

import { Badge } from '@rneui/themed';
import Animated, { useAnimatedStyle, withTiming, useSharedValue } from 'react-native-reanimated';

import type { BadgeProps } from '@rneui/themed';
import type { StyleProp, ViewStyle } from 'react-native';


interface AnimatedBadgeProps extends BadgeProps {
  containerStyle?: StyleProp<ViewStyle>;
}

const AnimatedBadge: React.FC<AnimatedBadgeProps> = ({ value, status, containerStyle, ...props }) => {
  const scale = useSharedValue(0);
  const opacity = useSharedValue(0);

  React.useEffect(() => {
    scale.value = withTiming(1, { duration: 500 });
    opacity.value = withTiming(1, { duration: 500 });
  }, []);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
    opacity: opacity.value,
  }));

  return (
    <Animated.View style={[animatedStyle, containerStyle]}>
      <Badge value={value} status={status} {...props} />
    </Animated.View>
  );
};

export default AnimatedBadge;
