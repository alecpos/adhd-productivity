import { useSharedValue, withTiming, useAnimatedStyle } from 'react-native-reanimated';

export const useLeaderboardAnimation = (delay: number) => {
  const opacity = useSharedValue(0);

  const animateEntry = () => {
    opacity.value = withTiming(1, { duration: 500 });
  };

  const entryStyle = useAnimatedStyle(() => ({
    opacity: opacity.value,
    transform: [{ translateY: 0 }],
  }));

  return { animateEntry, entryStyle };
};
