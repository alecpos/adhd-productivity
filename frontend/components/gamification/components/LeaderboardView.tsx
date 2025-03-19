import React from 'react';

import { ListItem, Avatar } from '@rneui/themed';
import { View, StyleSheet } from 'react-native';
import Animated, { useSharedValue, useAnimatedStyle, withDelay, withTiming } from 'react-native-reanimated';

interface LeaderboardViewProps {
  leaderboard: { user_id: string; rank: number }[];
}

const LeaderboardView: React.FC<LeaderboardViewProps> = ({ leaderboard }) => {
  return (
    <View style={styles.container}>
      {leaderboard.map((item, index) => {
        const opacity = useSharedValue(0);

        const animatedStyle = useAnimatedStyle(() => ({
          opacity: opacity.value,
          transform: [{ translateY: withTiming(0, { duration: 500 }) }],
        }));

        React.useEffect(() => {
          opacity.value = withDelay(index * 100, withTiming(1));
        }, []);

        return (
          <Animated.View key={index} style={[styles.listItem, animatedStyle]}>
            <ListItem>
              <Avatar
                rounded
                title={item.rank.toString()}
                containerStyle={styles.avatar}
              />
              <ListItem.Content>
                <ListItem.Title>{item.user_id}</ListItem.Title>
                <ListItem.Subtitle>Rank: {item.rank}</ListItem.Subtitle>
              </ListItem.Content>
            </ListItem>
          </Animated.View>
        );
      })}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginTop: 10,
  },
  listItem: {
    marginBottom: 10,
  },
  avatar: {
    backgroundColor: '#007bff',
  },
});

export default LeaderboardView;
