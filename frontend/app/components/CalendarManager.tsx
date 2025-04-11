import React, { useState, useEffect, useCallback } from 'react';

import { Text, Card, Input, Button, makeStyles, useTheme } from '@rneui/themed';
import { format } from 'date-fns';
import { View } from 'react-native';
import { Calendar } from 'react-native-calendars';


import { useCalendarService } from '@/app/hooks/useCalendarService';
import type { Task } from '@/app/types/task';

import { useAuth } from '../../contexts/AuthContext';
import { useCalendar } from '../../contexts/CalendarContext';


import { TaskCard } from './TaskCard';

import type { MarkedDates } from 'react-native-calendars';



interface DateData {
  year: number;
  month: number;
  day: number;
  timestamp: number;
  dateString: string;
}

const CalendarManager = () => {
    const { user } = useAuth();
    const { events, createEvent } = useCalendar();
    const [selectedDate, setSelectedDate] = useState(new Date());
    const [newTaskTitle, setNewTaskTitle] = useState('');
    const [newTaskDescription, setNewTaskDescription] = useState('');
    const { theme } = useTheme();
    const styles = useStyles();
    const calendarService = useCalendarService();
    const [tasks, setTasks] = useState<Task[]>([]);

    const fetchTasks = useCallback(async () => {
        if (!user?.id) return;

        try {
            const events = await calendarService.getEvents();
            const mappedTasks = events?.map(event => ({
                id: event.id,
                user_id: event.user_id,
                title: event.title,
                description: event.description || '',
                due_date: event.start_time,
                priority: 'MEDIUM',
                urgency: 0,
                impact: 0,
                effort: 0,
                completed: false,
                created_at: event.created_at,
                updated_at: event.updated_at
            } as Task)) || [];
            setTasks(mappedTasks);
        } catch (error) {
            console.error('Error fetching tasks:', error);
        }
    }, [user?.id, calendarService]);

    useEffect(() => {
        if (user?.id) {
            fetchTasks();
        }
    }, [user?.id]);

    const handleCreateTask = async () => {
        if (!user || !newTaskTitle) return;

        try {
            const startTime = selectedDate;
            const endTime = new Date(startTime.getTime() + 60 * 60 * 1000); // Add 1 hour

            await createEvent({
                title: newTaskTitle,
                description: newTaskDescription,
                start_time: startTime.toISOString(),
                end_time: endTime.toISOString(),
                user_id: user.id,
                event_type: "task",
                recurrence_type: "none"
            });
            setNewTaskTitle('');
            setNewTaskDescription('');
            fetchTasks();
        } catch (error) {
            console.error('Error creating task:', error);
        }
    };

    const getMarkedDates = () => {
        const markedDates: { [key: string]: { marked: boolean; dotColor: string } } = {};
        tasks.forEach((task) => {
            if (task.due_date) {
                const date = format(new Date(task.due_date), 'yyyy-MM-dd');
                markedDates[date] = {
                    marked: true,
                    dotColor: theme.colors.primary,
                };
            }
        });
        return markedDates;
    };

    const getTasksForSelectedDate = () => {
        return tasks.filter((task) => {
            if (!task.due_date) return false;
            const taskDate = format(new Date(task.due_date), 'yyyy-MM-dd');
            const selectedDateStr = format(selectedDate, 'yyyy-MM-dd');
            return taskDate === selectedDateStr;
        });
    };

    const handleDayPress = (day: DateData) => {
        setSelectedDate(new Date(day.timestamp));
    };

    const handleTaskComplete = async (taskId: string) => {
        try {
            await calendarService.updateEvent(taskId, {
                end_time: new Date().toISOString(),
                sync_status: 'pending'
            });
            fetchTasks();
        } catch (error) {
            console.error('Error completing task:', error);
        }
    };

    const handleTaskDelete = async (taskId: string) => {
        try {
            await calendarService.deleteEvent(taskId);
            fetchTasks();
        } catch (error) {
            console.error('Error deleting task:', error);
        }
    };

    return (
        <View style={styles.container}>
            <Calendar
                current={format(selectedDate, 'yyyy-MM-dd')}
                onDayPress={handleDayPress}
                markedDates={getMarkedDates()}
                theme={{
                    todayTextColor: theme.colors.primary,
                    selectedDayBackgroundColor: theme.colors.primary,
                    selectedDayTextColor: theme.colors.white,
                }}
            />

            <Card containerStyle={styles.card}>
                <Card.Title>Add New Task</Card.Title>
                <Input
                    placeholder="Task Title"
                    value={newTaskTitle}
                    onChangeText={setNewTaskTitle}
                />
                <Input
                    placeholder="Description"
                    value={newTaskDescription}
                    onChangeText={setNewTaskDescription}
                    multiline
                />
                <Button
                    title="Add Task"
                    onPress={handleCreateTask}
                />
            </Card>

            <Card containerStyle={styles.card}>
                <Card.Title>Tasks for {format(selectedDate, 'MMMM d, yyyy')}</Card.Title>
                {getTasksForSelectedDate().map((task) => (
                    <TaskCard
                        key={task.id}
                        task={task}
                        onComplete={() => handleTaskComplete(task.id)}
                        onDelete={() => handleTaskDelete(task.id)}
                    />
                ))}
                {getTasksForSelectedDate().length === 0 && (
                    <Text style={styles.noTasks}>No tasks for this date</Text>
                )}
            </Card>
        </View>
    );
};

export { CalendarManager };
export default CalendarManager;

const useStyles = makeStyles((theme) => ({
    container: {
        flex: 1,
    },
    card: {
        marginVertical: theme.spacing.sm,
    },
    noTasks: {
        textAlign: 'center',
        color: theme.colors.grey3,
        padding: theme.spacing.md,
    },
}));
