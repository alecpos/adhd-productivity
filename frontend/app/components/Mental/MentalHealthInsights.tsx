import React, { useEffect, useState } from 'react';

import { Text, Card, makeStyles, useTheme } from '@rneui/themed';
import { View, ScrollView, Dimensions } from 'react-native';
import { LineChart } from 'react-native-chart-kit';

import type { MentalHealthStats } from '@/app/services/mental-health';
import { useMentalHealth } from '@/contexts/MentalHealthContext';

interface MentalHealthInsightsProps {
    userId: string;
}

export default function MentalHealthInsights({ userId }: MentalHealthInsightsProps) {
    const [stats, setStats] = useState<MentalHealthStats | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const { getStats } = useMentalHealth();
    const styles = useStyles();
    const { theme } = useTheme();
    const screenWidth = Dimensions.get('window').width;

    useEffect(() => {
        const loadStats = async () => {
            try {
                setLoading(true);
                const data = await getStats();
                setStats(data);
            } catch (error) {
                console.error('Error loading mental health stats:', error);
                setError('Failed to load mental health insights');
            } finally {
                setLoading(false);
            }
        };
        loadStats();
    }, [userId, getStats]);

    if (loading) {
        return <Text>Loading insights...</Text>;
    }

    if (error) {
        return <Text style={styles.error}>{error}</Text>;
    }

    if (!stats) {
        return <Text>No data available</Text>;
    }

    // Extract mood history from recent_moods
    const moodData = stats.recent_moods.map(log => log.mood);
    const dates = stats.recent_moods.map(log => new Date(log.date).toLocaleDateString());

    return (
        <ScrollView style={styles.container}>
            <Card containerStyle={styles.card}>
                <Card.Title>Mental Health Overview</Card.Title>
                <View style={styles.statsContainer}>
                    <View style={styles.statItem}>
                        <Text style={styles.statLabel}>Average Mood</Text>
                        <Text style={styles.statValue}>{stats.mood_average.toFixed(1)}/10</Text>
                    </View>
                    <View style={styles.statItem}>
                        <Text style={styles.statLabel}>Current Streak</Text>
                        <Text style={styles.statValue}>{stats.streak} days</Text>
                    </View>
                </View>
                {moodData.length > 0 && (
                    <View style={styles.chartContainer}>
                        <Text style={styles.chartTitle}>Mood History</Text>
                        <LineChart
                            data={{
                                labels: dates,
                                datasets: [{
                                    data: moodData
                                }]
                            }}
                            width={screenWidth - 60}
                            height={220}
                            chartConfig={{
                                backgroundColor: theme.colors.background,
                                backgroundGradientFrom: theme.colors.background,
                                backgroundGradientTo: theme.colors.background,
                                decimalPlaces: 1,
                                color: (opacity = 1) => theme.colors.primary,
                                labelColor: (opacity = 1) => theme.colors.grey0,
                                style: {
                                    borderRadius: 16
                                }
                            }}
                            bezier
                            style={{
                                marginVertical: 8,
                                borderRadius: 16
                            }}
                        />
                    </View>
                )}
                {stats.most_common_activities.length > 0 && (
                    <View style={styles.activitiesContainer}>
                        <Text style={styles.sectionTitle}>Most Common Activities</Text>
                        {stats.most_common_activities.map((activity, index) => (
                            <Text key={index} style={styles.activity}>• {activity}</Text>
                        ))}
                    </View>
                )}
            </Card>
        </ScrollView>
    );
}

const useStyles = makeStyles((theme) => ({
    container: {
        flex: 1,
    },
    card: {
        margin: theme.spacing.md,
        borderRadius: theme.spacing.sm,
    },
    statsContainer: {
        flexDirection: 'row',
        justifyContent: 'space-around',
        marginBottom: theme.spacing.lg,
    },
    statItem: {
        alignItems: 'center',
    },
    statLabel: {
        color: theme.colors.grey2,
        fontSize: 14,
        marginBottom: theme.spacing.xs,
    },
    statValue: {
        fontSize: 24,
        fontWeight: 'bold',
        color: theme.colors.primary,
    },
    chartContainer: {
        marginTop: theme.spacing.lg,
    },
    chartTitle: {
        fontSize: 16,
        fontWeight: 'bold',
        marginBottom: theme.spacing.sm,
        textAlign: 'center',
    },
    activitiesContainer: {
        marginTop: theme.spacing.lg,
    },
    sectionTitle: {
        fontSize: 16,
        fontWeight: 'bold',
        marginBottom: theme.spacing.sm,
    },
    activity: {
        fontSize: 14,
        color: theme.colors.grey1,
        marginBottom: theme.spacing.xs,
    },
    error: {
        color: theme.colors.error,
        textAlign: 'center',
        margin: theme.spacing.lg,
    },
})); 