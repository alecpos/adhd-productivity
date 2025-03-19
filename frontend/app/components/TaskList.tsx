import React, { useState } from 'react';

import { Text, Button, SearchBar, makeStyles } from '@rneui/themed';
import { format } from 'date-fns';
import { View, FlatList } from 'react-native';

import type { Task } from '../types/task';

type SortField = 'title' | 'dueDate';
type SortDirection = 'asc' | 'desc';
type FilterType = string;

interface TaskListProps {
    tasks: Task[];
    onCompleteTask: (taskId: string) => Promise<void>;
    onDeleteTask: (taskId: string) => Promise<void>;
    loading?: boolean;
}

const useStyles = makeStyles((theme) => ({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  taskItem: {
    padding: theme.spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.grey5,
  },
  taskTitle: {
    fontSize: theme.fontSize.lg,
    fontWeight: 'bold',
    color: theme.colors.primary,
  },
  taskDescription: {
    fontSize: theme.fontSize.md,
    color: theme.colors.grey1,
    marginTop: theme.spacing.xs,
  },
  taskActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: theme.spacing.sm,
  },
  sortControls: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    padding: theme.spacing.sm,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: theme.spacing.lg,
  },
  emptyText: {
    fontSize: theme.fontSize.lg,
    color: theme.colors.grey2,
    textAlign: 'center',
  },
}));

export const TaskList: React.FC<TaskListProps> = ({ 
    tasks = [], 
    onCompleteTask, 
    onDeleteTask, 
    loading = false 
}) => {
    const [sortField, setSortField] = useState<SortField>('dueDate');
    const [sortDirection, setSortDirection] = useState<SortDirection>('asc');
    const [filter, setFilter] = useState<FilterType>('');
    const styles = useStyles();

    const renderItem = ({ item }: { item: Task }) => (
        <View style={styles.taskItem}>
            <Text style={styles.taskTitle}>{item.title}</Text>
            {item.description && (
                <Text style={styles.taskDescription}>{item.description}</Text>
            )}
            {item.due_date && (
                <Text>Due: {format(new Date(item.due_date), 'PPP')}</Text>
            )}
            <View style={styles.taskActions}>
                <Button
                    title="Complete"
                    onPress={() => onCompleteTask(item.id)}
                />
                <Button
                    title="Delete"
                    onPress={() => onDeleteTask(item.id)}
                />
            </View>
        </View>
    );

    if (loading) {
        return (
            <View style={styles.loadingContainer}>
                <Text>Loading tasks...</Text>
            </View>
        );
    }

    const filteredTasks = (tasks || []).filter(task => {
        const searchTerm = (filter || '').toLowerCase();
        const title = (task.title || '').toLowerCase();
        const description = (task.description || '').toLowerCase();
        
        return title.includes(searchTerm) || description.includes(searchTerm);
    });

    const sortedTasks = [...filteredTasks].sort((a, b) => {
        if (sortField === 'title') {
            const titleA = (a.title || '').toLowerCase();
            const titleB = (b.title || '').toLowerCase();
            return sortDirection === 'asc' 
                ? titleA.localeCompare(titleB)
                : titleB.localeCompare(titleA);
        } else {
            const dateA = a.due_date ? new Date(a.due_date) : new Date(0);
            const dateB = b.due_date ? new Date(b.due_date) : new Date(0);
            return sortDirection === 'asc' 
                ? dateA.getTime() - dateB.getTime()
                : dateB.getTime() - dateA.getTime();
        }
    });

    if (!loading && (!tasks || tasks.length === 0)) {
        return (
            <View style={styles.emptyContainer}>
                <Text style={styles.emptyText}>No tasks found</Text>
            </View>
        );
    }

    return (
        <View style={styles.container}>
            <SearchBar
                placeholder="Search tasks..."
                onChangeText={setFilter}
                value={filter || ''}
                platform="default"
            />
            <View style={styles.sortControls}>
                <Button
                    title={`Sort by ${sortField === 'dueDate' ? 'Due Date' : 'Title'}`}
                    onPress={() => setSortField(sortField === 'dueDate' ? 'title' : 'dueDate')}
                />
                <Button
                    title={`Order ${sortDirection === 'asc' ? '↑' : '↓'}`}
                    onPress={() => setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')}
                />
            </View>
            <FlatList
                data={sortedTasks}
                renderItem={renderItem}
                keyExtractor={item => item.id}
            />
        </View>
    );
}; 