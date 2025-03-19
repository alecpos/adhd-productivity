import React from 'react';

import { Text, Card } from '@rneui/themed';
import { View, StyleSheet, ScrollView } from 'react-native';

import { useGamification } from '@/contexts/GamificationContxt';

export default function GamificationDashboard() {
    const { dashboard, loading, error } = useGamification();

    if (loading) {
        return (
            <View style={styles.container}>
                <Text>Loading...</Text>
            </View>
        );
    }

    if (error) {
        return (
            <View style={styles.errorContainer}>
                <Text style={styles.errorText}>{error}</Text>
            </View>
        );
    }

    if (!dashboard) {
        return (
            <View style={styles.container}>
                <Text>No gamification data available</Text>
            </View>
        );
    }

    return (
        <ScrollView style={styles.container}>
            <Card>
                <Card.Title>Your Progress</Card.Title>
                <View style={styles.statsContainer}>
                    <View style={styles.statItem}>
                        <Text h4>{dashboard.points.total_points}</Text>
                        <Text>Points</Text>
                    </View>
                    <View style={styles.statItem}>
                        <Text h4>{dashboard.points.level}</Text>
                        <Text>Level</Text>
                    </View>
                    <View style={styles.statItem}>
                        <Text h4>{dashboard.streaks?.current_streak || 0}</Text>
                        <Text>Current Streak</Text>
                    </View>
                    <View style={styles.statItem}>
                        <Text h4>{dashboard.streaks?.longest_streak || 0}</Text>
                        <Text>Best Streak</Text>
                    </View>
                </View>
            </Card>

            <Card>
                <Card.Title>Badges</Card.Title>
                {dashboard.badges.length > 0 ? (
                    dashboard.badges.map((badge) => (
                        <View key={badge.id} style={styles.badge}>
                            <Text style={styles.badgeTitle}>{badge.name}</Text>
                            <Text style={styles.badgeDescription}>{badge.description}</Text>
                            <Text style={styles.badgeLevel}>Level {badge.level}</Text>
                        </View>
                    ))
                ) : (
                    <Text style={styles.emptyText}>No badges earned yet</Text>
                )}
            </Card>

            <Card>
                <Card.Title>Achievements</Card.Title>
                {dashboard.achievements.length > 0 ? (
                    dashboard.achievements.map((achievement) => (
                        <View key={achievement.id} style={styles.achievement}>
                            <Text style={styles.achievementTitle}>{achievement.name}</Text>
                            <Text style={styles.achievementDescription}>{achievement.description}</Text>
                            <View style={styles.achievementProgress}>
                                <Text>Progress: {achievement.meta_data.progress}%</Text>
                                {achievement.meta_data.completed && (
                                    <Text style={styles.completedText}>✓ Completed</Text>
                                )}
                            </View>
                        </View>
                    ))
                ) : (
                    <Text style={styles.emptyText}>No achievements yet</Text>
                )}
            </Card>

            <Card>
                <Card.Title>Leaderboard</Card.Title>
                {dashboard.leaderboard.entries.length > 0 ? (
                    dashboard.leaderboard.entries.map((entry, index) => (
                        <View key={entry.user_id} style={styles.leaderboardEntry}>
                            <Text style={styles.rank}>#{entry.rank}</Text>
                            <Text style={styles.score}>{entry.score} pts</Text>
                        </View>
                    ))
                ) : (
                    <Text style={styles.emptyText}>No leaderboard data available</Text>
                )}
            </Card>
        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
    },
    errorContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    errorText: {
        color: 'red',
        fontSize: 16,
    },
    statsContainer: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        justifyContent: 'space-around',
        marginVertical: 10,
    },
    statItem: {
        alignItems: 'center',
        marginVertical: 5,
        minWidth: '40%',
    },
    badge: {
        marginVertical: 8,
        padding: 8,
        backgroundColor: '#f5f5f5',
        borderRadius: 8,
    },
    badgeTitle: {
        fontSize: 16,
        fontWeight: 'bold',
    },
    badgeDescription: {
        fontSize: 14,
        color: '#666',
        marginTop: 4,
    },
    badgeLevel: {
        fontSize: 12,
        color: '#888',
        marginTop: 4,
    },
    achievement: {
        marginVertical: 8,
        padding: 8,
        backgroundColor: '#f5f5f5',
        borderRadius: 8,
    },
    achievementTitle: {
        fontSize: 16,
        fontWeight: 'bold',
    },
    achievementDescription: {
        fontSize: 14,
        color: '#666',
        marginTop: 4,
    },
    achievementProgress: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginTop: 4,
    },
    completedText: {
        color: 'green',
        fontWeight: 'bold',
    },
    leaderboardEntry: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingVertical: 8,
        borderBottomWidth: 1,
        borderBottomColor: '#eee',
    },
    rank: {
        fontSize: 16,
        fontWeight: 'bold',
    },
    score: {
        fontSize: 16,
    },
    emptyText: {
        textAlign: 'center',
        color: '#666',
        fontStyle: 'italic',
        marginVertical: 10,
    },
}); 