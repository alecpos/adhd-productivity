import React, { useState } from 'react';

import { Text, Card, Button, Input, makeStyles } from '@rneui/themed';
import { View } from 'react-native';


import { useBlockSchedule } from '@/app/hooks/useBlockSchedule';
import type { BlockSchedule } from '@/app/types/block-schedule';
import { api } from '@/lib/api';

import { useAuth } from '../../contexts/AuthContext';

export function BlockScheduler() {
    const { user } = useAuth();
    const { schedules, loading, createSchedule, updateSchedule, deleteSchedule } = useBlockSchedule();
    const [newBlockName, setNewBlockName] = useState('');
    const [newBlockDuration, setNewBlockDuration] = useState('');
    const styles = useStyles();

    const handleCreateBlock = async () => {
        if (!user || !newBlockName || !newBlockDuration) return;

        try {
            await createSchedule({
                name: newBlockName,
                duration: parseInt(newBlockDuration),
                startTime: new Date().toISOString(),
                endTime: new Date(Date.now() + parseInt(newBlockDuration) * 60000).toISOString(),
            });
            setNewBlockName('');
            setNewBlockDuration('');
        } catch (error) {
            console.error('Error creating block:', error);
        }
    };

    const handleUpdateBlock = async (id: string, data: Partial<BlockSchedule>) => {
        try {
            await updateSchedule(id, data);
        } catch (error) {
            console.error('Error updating block:', error);
        }
    };

    const handleDeleteBlock = async (id: string) => {
        try {
            await deleteSchedule(id);
        } catch (error) {
            console.error('Error deleting block:', error);
        }
    };

    return (
        <View>
            <Card>
                <Card.Title>Create New Block</Card.Title>
                <Input
                    placeholder="Block Name"
                    value={newBlockName}
                    onChangeText={setNewBlockName}
                />
                <Input
                    placeholder="Duration (minutes)"
                    value={newBlockDuration}
                    onChangeText={setNewBlockDuration}
                    keyboardType="numeric"
                />
                <Button
                    title="Create Block"
                    onPress={handleCreateBlock}
                    loading={loading}
                    disabled={!newBlockName || !newBlockDuration || loading}
                />
            </Card>

            {schedules.map((block: BlockSchedule) => (
                <Card key={block.id} containerStyle={styles.card}>
                    <View style={styles.blockHeader}>
                        <Text style={styles.blockTitle}>{block.name}</Text>
                        <Text style={styles.duration}>{block.duration} minutes</Text>
                    </View>
                    <View style={styles.blockActions}>
                        <Button
                            title="Edit"
                            type="outline"
                            onPress={() => handleUpdateBlock(block.id, {
                                // Add edit functionality
                            })}
                        />
                        <Button
                            title="Delete"
                            type="outline"
                            onPress={() => handleDeleteBlock(block.id)}
                        />
                    </View>
                </Card>
            ))}
        </View>
    );
}

const useStyles = makeStyles((theme) => ({
    card: {
        marginVertical: theme.spacing.sm,
    },
    blockHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: theme.spacing.sm,
    },
    blockTitle: {
        fontSize: theme.fontSize.lg,
        fontWeight: 'bold',
        color: theme.colors.primary,
    },
    duration: {
        fontSize: theme.fontSize.md,
        color: theme.colors.grey3,
    },
    blockActions: {
        flexDirection: 'row',
        justifyContent: 'space-around',
        marginTop: theme.spacing.sm,
    },
})); 