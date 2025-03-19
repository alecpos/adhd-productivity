import { useSharedValue, withSpring, useAnimatedStyle } from 'react-native-reanimated';

export const useStreakAnimation = () => {
  const scale = useSharedValue(1);

  const animateStreak = () => {
    scale.value = withSpring(1.2, {}, () => {
      scale.value = withSpring(1);
    });
  };

  const streakStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  return { animateStreak, streakStyle };
};
