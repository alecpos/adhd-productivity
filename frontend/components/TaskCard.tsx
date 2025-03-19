import React from 'react';

import { makeStyles, useTheme } from '@rneui/themed';
import { View, Text, Button } from 'react-native';

import { useHyperfocus } from '../contexts/HyperfocusContext';
import { StartSessionRequest } from '../core/api/services/hyperfocusService';

import type { Task } from '../core/api/services/taskService';

interface TaskCardProps {
    task: Task;
    onComplete: () => void;
    onDelete: () => void;
}

const useStyles = makeStyles((theme) => ({
    card: {
        backgroundColor: theme.colors.background,
        padding: theme.spacing.md,
        borderRadius: theme.borderRadius.md,
        shadowColor: theme.colors.black,
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
    },
    header: {
        marginBottom: theme.spacing.sm,
    },
    title: {
        fontSize: theme.fontSize.lg,
        fontWeight: 'bold',
        color: theme.colors.text,
    },
    dueDate: {
        fontSize: theme.fontSize.sm,
        color: theme.colors.grey3,
    },
    description: {
        fontSize: theme.fontSize.md,
        color: theme.colors.text,
        marginBottom: theme.spacing.md,
    },
    actions: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginBottom: theme.spacing.md,
    },
    priority: {
        fontSize: theme.fontSize.sm,
        color: theme.colors.text,
    },
    energy: {
        marginTop: theme.spacing.sm,
        fontSize: theme.fontSize.sm,
        color: theme.colors.grey3,
    },
}));

export const TaskCard = ({ task, onComplete, onDelete }: TaskCardProps) => {
    const { startSession } = useHyperfocus() as { startSession: (data: number) => Promise<void> };
    const styles = useStyles();
    const { theme } = useTheme();

    const handleStartSession = async () => {
        try {
            await startSession(task.estimated_duration || 25);
        } catch (error) {
            console.error('Failed to start focus session:', error);
        }
    };

    return (
        <View style={styles.card}>
            <View style={styles.header}>
                <Text style={styles.title}>{task.title}</Text>
                {task.due_date && (
                    <Text style={styles.dueDate}>{`Due: ${new Date(task.due_date).toLocaleDateString()}`}</Text>
                )}
            </View>
            {task.description && (
                <Text style={styles.description}>{task.description}</Text>
            )}
            <View style={styles.actions}>
                <Button 
                    title={task.completed ? "Completed" : "Complete"} 
                    onPress={onComplete}
                    disabled={task.completed}
                />
                <Button title="Delete" onPress={onDelete} />
                <Button 
                    title="Start Focus" 
                    onPress={handleStartSession}
                />
            </View>
            <Text style={styles.priority}>{`Priority: ${task.priority}`}</Text>
            {task.energy_required && (
                <Text style={styles.energy}>{`Energy Required: ${task.energy_required}`}</Text>
            )}
        </View>
    );
};
