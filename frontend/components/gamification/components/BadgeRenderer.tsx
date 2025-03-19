import React from 'react';

import { Badge } from '@rneui/themed';
import { View, StyleSheet } from 'react-native';
import Animated, { useSharedValue, useAnimatedStyle, withTiming, withDelay } from 'react-native-reanimated';

interface BadgeRendererProps {
  badges: string[];
}

const BadgeRenderer: React.FC<BadgeRendererProps> = ({ badges }) => {
  return (
    <View style={styles.container}>
      {badges.map((badge, index) => {
        const scale = useSharedValue(0);

        const animatedStyle = useAnimatedStyle(() => ({
          transform: [{ scale: scale.value }],
        }));

        React.useEffect(() => {
          scale.value = withDelay(index * 200, withTiming(1, { duration: 500 }));
        }, []);

        return (
          <Animated.View key={index} style={[styles.badge, animatedStyle]}>
            <Badge value={badge} status="primary" />
          </Animated.View>
        );
      })}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 10,
  },
  badge: {
    margin: 5,
  },
});

export default BadgeRenderer;
