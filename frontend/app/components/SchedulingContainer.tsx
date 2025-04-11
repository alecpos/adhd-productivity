import React, { useState, useEffect } from 'react';

import { Text, Button } from '@rneui/themed';
import { View, StyleSheet } from 'react-native';
import Toast from 'react-native-toast-message';

import { schedulingService } from '@/app/services/schedulingService';

import { useAuth } from '../../contexts/AuthContext';



import AISchedulingAssistant from './AISchedulingAssistant';
import { BlockScheduler } from './BlockScheduler';

interface SchedulingContainerProps {
    onScheduleCreated?: () => void;
}

export default function SchedulingContainer({ onScheduleCreated }: SchedulingContainerProps) {
    const { user } = useAuth();
    const [loading, setLoading] = useState(false);

    const handleScheduleCreation = async () => {
        if (!user?.id) {
            Toast.show({
                type: 'error',
                text1: 'Error',
                text2: 'Please log in to create a schedule',
            });
            return;
        }

        setLoading(true);
        try {
            await schedulingService.createSchedule(user.id);
            Toast.show({
                type: 'success',
                text1: 'Success',
                text2: 'Schedule created successfully',
            });
            onScheduleCreated?.();
        } catch (error: any) {
            Toast.show({
                type: 'error',
                text1: 'Error',
                text2: error?.message || 'Failed to create schedule',
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <View style={styles.container}>
            <AISchedulingAssistant />
            <BlockScheduler />
            <Button
                title={loading ? "Creating..." : "Create Schedule"}
                onPress={handleScheduleCreation}
                loading={loading}
                disabled={loading}
            />
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        padding: 16,
    },
});
