import React from "react";

import { Card, Text } from "@rneui/themed";
import { View, StyleSheet, ScrollView } from "react-native";

import BadgeRenderer from "./BadgeRenderer";
import LeaderboardView from "./LeaderboardView";

type GamificationDashboardProps = {
  streaks: {
    current_streak: number;
    highest_streak: number;
    badges: string[];
  };
  leaderboard: {
    group_name: string;
    rank: number;
    user_id: string;
  }[];
};

const GamificationDashboard: React.FC<GamificationDashboardProps> = ({ streaks, leaderboard }) => {
  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Card containerStyle={styles.card}>
        <Text h4 style={styles.title}>Your Streaks</Text>
        <Text style={styles.text}>Current Streak: {streaks.current_streak}</Text>
        <Text style={styles.text}>Highest Streak: {streaks.highest_streak}</Text>
        <BadgeRenderer badges={streaks.badges} />
      </Card>
      <Card containerStyle={styles.card}>
        <Text h4 style={styles.title}>Leaderboard</Text>
        <LeaderboardView leaderboard={leaderboard} />
      </Card>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 20,
    backgroundColor: "#f9f9f9",
    flexGrow: 1,
  },
  card: {
    marginBottom: 20,
    borderRadius: 10,
    padding: 15,
    elevation: 3,
  },
  title: {
    fontSize: 20,
    fontWeight: "bold",
    marginBottom: 10,
  },
  text: {
    fontSize: 16,
    marginBottom: 5,
  },
});

export default GamificationDashboard;
