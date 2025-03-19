import React, { useState } from 'react';

import { Text } from '@rneui/themed';
import { ScrollView, StyleSheet, View } from 'react-native';

import type { CreateMentalHealthLog } from '@/app/types/mental-health';

import { useAuth } from '../../contexts/AuthContext';
import { useMentalHealth } from '../../contexts/MentalHealthContext';
import MentalHealthInsights from '../components/Mental/MentalHealthInsights';
import MentalHealthLogForm from '../components/Mental/MentalHealthLogForm';


export default function MentalHealthScreen() {
    const { user } = useAuth();
    const { createLog } = useMentalHealth();
    const [refreshKey, setRefreshKey] = useState(0);
    const [error, setError] = useState<string | null>(null);

    if (!user) {
        return (
            <View style={styles.container}>
                <Text>Please log in to access mental health tracking.</Text>
            </View>
        );
    }

    const handleLogSubmit = async (data: Partial<CreateMentalHealthLog>) => {
        console.debug('Handling mental health log submission:', { ...data, userId: user.id });
        try {
            await createLog({
                ...data,
                userId: user.id
            });
            console.debug('Mental health log submitted successfully');
            setRefreshKey(prev => prev + 1);
            setError(null);
        } catch (err) {
            console.error('Error submitting mental health log:', err);
            setError(err instanceof Error ? err.message : 'Failed to submit log');
        }
    };

    return (
        <ScrollView style={styles.container}>
            <View style={styles.section}>
                <Text h4 style={styles.sectionTitle}>Mental Health Tracking</Text>
                {error && (
                    <Text style={styles.error}>{error}</Text>
                )}
                <MentalHealthLogForm 
                    onSubmit={handleLogSubmit}
                    onSuccess={() => setError(null)}
                />
                <MentalHealthInsights 
                    userId={user.id}
                    key={refreshKey} 
                />
            </View>
        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
    },
    section: {
        padding: 20,
    },
    sectionTitle: {
        marginBottom: 20,
    },
    error: {
        color: 'red',
        marginBottom: 10,
    }
}); 