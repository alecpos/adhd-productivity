// React and core imports
import React, { useState, useEffect } from 'react';

// Third-party imports
import { Text, Button, Card, Input, Slider, Chip, Icon, makeStyles, useTheme } from '@rneui/themed';
import { format } from 'date-fns';
import { View, ScrollView } from 'react-native';
import Toast from 'react-native-toast-message';
import { useDispatch, useSelector } from 'react-redux';

import huggingfaceService from '@/app/services/huggingface';
import { TaskService } from '@/app/services/task';
import { TaskStatus, TaskPriority } from '@/types/task';
import type { Task as BackendTask } from '@/types/task';

// Local imports
import { useAuth } from '../../contexts/AuthContext';
import { addTask, setTasks, setLoading, setError, updateTask, deleteTask } from '../store/slices/taskSlice';

// Service imports

// Type imports
import type { RootState } from '../store';
import type { Task as FrontendTask, SubTask } from '../store/slices/taskSlice';

interface CreateTaskData {
  title: string;
  description?: string;
  status: TaskStatus;
  priority: TaskPriority;
  due_date?: string;
  estimated_duration?: number;
  energy_required?: number;
  difficulty_rating?: number;
  meta_data?: {
    color: string;
    subtasks: SubTask[];
    reminders: string[];
    recurring?: boolean;
    startTime: string;
    endTime: string;
  };
  user_id: string;
  completed: boolean;
}

interface NewTaskForm {
  title?: string;
  description?: string;
  startTime?: string;
  endTime?: string;
  difficulty: number;
  energyRequired: number;
  subtasks: SubTask[];
  reminders: string[];
  recurring?: boolean;
}

interface ErrorResponse {
  detail?: string;
  message?: string;
  statusText?: string;
}

const transformServiceTaskToComponentTask = (serviceTask: BackendTask): FrontendTask => {
  const metaData = serviceTask.meta_data as {
    color?: string;
    subtasks?: SubTask[];
    reminders?: string[];
    recurring?: boolean;
    startTime?: string;
    endTime?: string;
  } ?? {};

  return {
    id: serviceTask.id,
    title: serviceTask.title,
    description: serviceTask.description,
    startTime: metaData?.startTime ?? new Date().toISOString(),
    endTime: serviceTask.due_date ?? new Date().toISOString(),
    difficulty: serviceTask.difficulty_rating ?? 3,
    energyRequired: serviceTask.energy_required ?? 5,
    subtasks: metaData?.subtasks ?? [],
    completed: serviceTask.completed,
    recurring: metaData?.recurring,
    reminders: metaData?.reminders ?? [],
    color: metaData?.color,
    userId: serviceTask.user_id
  };
};

export default function CalendarManagement(): JSX.Element {
  const { user } = useAuth();
  const dispatch = useDispatch();
  const tasks = useSelector((state: RootState) => state.tasks.tasks);
  const loading = useSelector((state: RootState) => state.tasks.loading);
  const [_selectedTask, setSelectedTask] = useState<FrontendTask | null>(null);
  const [showTaskForm, setShowTaskForm] = useState(false);
  const [newTask, setNewTask] = useState<NewTaskForm>({
    difficulty: 3,
    energyRequired: 5,
    subtasks: [],
    reminders: [],
  });
  const [aiSuggestions, setAiSuggestions] = useState<string[]>([]);
  const taskService = user?.id ? new TaskService(user.id) : null;
  const { theme } = useTheme();
  const styles = useStyles(theme);

  useEffect(() => {
    if (user?.id && taskService) {
      void loadTasks();
    }
  }, [user, taskService]);

  const loadTasks = async (): Promise<void> => {
    if (!taskService) return;
    
    dispatch(setLoading(true));
    try {
      const serviceTasks = await taskService.getTasks();
      const componentTasks = serviceTasks.map(transformServiceTaskToComponentTask);
      dispatch(setTasks(componentTasks));
    } catch (_error) {
      dispatch(setError('Failed to load tasks'));
      Toast.show({
        type: 'error',
        text1: 'Error',
        text2: 'Failed to load tasks',
      });
    } finally {
      dispatch(setLoading(false));
    }
  };

  const handleAddSubtask = (): void => {
    if (!newTask.title) {
      Toast.show({
        type: 'error',
        text1: 'Error',
        text2: 'Please enter a task title first',
      });
      return;
    }

    void getTaskBreakdownSuggestions(newTask.title, newTask.description ?? '');
  };

  const getTaskBreakdownSuggestions = async (title: string, description: string): Promise<void> => {
    try {
      const prompt = `Break down this ADHD task into smaller, manageable subtasks. Consider executive function challenges.
      Task: ${title}
      Description: ${description}`;

      const suggestions = await huggingfaceService.getTaskBreakdown(prompt);
      setAiSuggestions(suggestions);
    } catch (_error) {
      Toast.show({
        type: 'error',
        text1: 'Error',
        text2: 'Failed to get AI suggestions',
      });
    }
  };

  const addSubtaskFromSuggestion = (suggestion: string): void => {
    const newSubtask: SubTask = {
      id: Math.random().toString(),
      title: suggestion,
      completed: false,
      estimatedDuration: 15, // Default 15 minutes
    };

    setNewTask(prev => ({
      ...prev,
      subtasks: [...(prev.subtasks ?? []), newSubtask],
    }));
  };

  const handleSaveTask = async (): Promise<void> => {
    if (!taskService || !user?.id) {
      Toast.show({
        type: 'error',
        text1: 'System Error',
        text2: 'Please try again or contact support if the issue persists',
      });
      return;
    }

    // Enhanced input validation
    const validationErrors: string[] = [];
    
    if (!newTask.title?.trim()) {
      validationErrors.push('Task title is required');
    } else if (newTask.title.trim().length < 3) {
      validationErrors.push('Task title must be at least 3 characters long');
    }

    if (!newTask.startTime || !newTask.endTime) {
      validationErrors.push('Start and end times are required');
    } else {
      const startDate = new Date(newTask.startTime);
      const endDate = new Date(newTask.endTime);
      const now = new Date();

      if (startDate < now) {
        validationErrors.push('Start time cannot be in the past');
      }
      if (endDate <= startDate) {
        validationErrors.push('End time must be after start time');
      }
    }

    if (newTask.difficulty < 1 || newTask.difficulty > 5) {
      validationErrors.push('Difficulty must be between 1 and 5');
    }

    if (newTask.energyRequired < 1 || newTask.energyRequired > 10) {
      validationErrors.push('Energy required must be between 1 and 10');
    }

    if (validationErrors.length > 0) {
      Toast.show({
        type: 'error',
        text1: 'Validation Error',
        text2: validationErrors.length > 1 
          ? `${validationErrors[0]} (and ${validationErrors.length - 1} more errors)`
          : validationErrors[0],
      });
      return;
    }

    try {
      // Since we've already validated title exists above, we can safely use nullish coalescing
      const sanitizedTitle = newTask.title?.trim().replace(/[<>]/g, '') ?? 'Untitled Task';
      const sanitizedDesc = newTask.description?.trim().replace(/[<>]/g, '') ?? '';

      const taskColor = getTaskColor(newTask.difficulty ?? 3, newTask.energyRequired ?? 5);
      const taskData: CreateTaskData = {
        title: sanitizedTitle,
        description: sanitizedDesc,
        status: TaskStatus.TODO,
        priority: TaskPriority.MEDIUM,
        due_date: newTask.endTime!,
        estimated_duration: newTask.subtasks.reduce((acc, st) => acc + st.estimatedDuration, 0),
        energy_required: newTask.energyRequired ?? 5,
        difficulty_rating: newTask.difficulty ?? 3,
        meta_data: {
          color: taskColor,
          subtasks: newTask.subtasks ?? [],
          reminders: newTask.reminders ?? [],
          recurring: newTask.recurring,
          startTime: newTask.startTime!,
          endTime: newTask.endTime!
        },
        user_id: user.id,
        completed: false
      };
      
      const response = await taskService.createTask(taskData);
      if (response?.data === undefined) {
        throw new Error('Failed to save task');
      }
      const savedComponentTask = transformServiceTaskToComponentTask(response.data);
      dispatch(addTask(savedComponentTask));
      
      Toast.show({
        type: 'success',
        text1: 'Success',
        text2: 'Task created successfully',
      });

      setShowTaskForm(false);
      setNewTask({
        difficulty: 3,
        energyRequired: 5,
        subtasks: [],
        reminders: [],
      });
      setAiSuggestions([]);
    } catch (error) {
      // Enhanced error handling
      let errorMessage = 'Failed to save task';
      if (error instanceof Error) {
        errorMessage = error.message;
      } else if (error instanceof Response) {
        try {
          const data = await error.json() as ErrorResponse;
          errorMessage = data.detail ?? data.message ?? errorMessage;
        } catch {
          // If JSON parsing fails, use the status text
          errorMessage = error.statusText ?? errorMessage;
        }
      }

      Toast.show({
        type: 'error',
        text1: 'Error',
        text2: errorMessage,
        visibilityTime: 4000, // Show longer for error messages
        autoHide: true,
        topOffset: 30,
        bottomOffset: 40,
      });
    }
  };

  const getTaskColor = (difficulty: number, energy: number): string => {
    // Color scheme based on task difficulty and energy requirements
    if (difficulty >= 4 && energy >= 7) return '#ff4444'; // Red for high difficulty & energy
    if (difficulty >= 4) return '#ff8800'; // Orange for high difficulty
    if (energy >= 7) return '#ffbb33'; // Yellow for high energy
    return '#00C851'; // Green for manageable tasks
  };

  const handleUpdateTask = async (taskId: string, updates: Partial<FrontendTask>): Promise<void> => {
    if (!taskService) return;

    try {
      const taskData = {
        ...updates,
        meta_data: {
          color: updates.color,
          subtasks: updates.subtasks,
          reminders: updates.reminders,
          recurring: updates.recurring,
          startTime: updates.startTime,
          endTime: updates.endTime
        },
      };
      
      const updatedServiceTask = await taskService.updateTask(taskId, taskData);
      const updatedComponentTask = transformServiceTaskToComponentTask(updatedServiceTask.data);
      dispatch(updateTask(updatedComponentTask));
      
      Toast.show({
        type: 'success',
        text1: 'Success',
        text2: 'Task updated successfully',
      });
    } catch (_error) {
      Toast.show({
        type: 'error',
        text1: 'Error',
        text2: 'Failed to update task',
      });
    }
  };

  const handleDeleteTask = async (taskId: string): Promise<void> => {
    if (!taskService) return;

    try {
      await taskService.deleteTask(taskId);
      dispatch(deleteTask(taskId));
      
      Toast.show({
        type: 'success',
        text1: 'Success',
        text2: 'Task deleted successfully',
      });
    } catch (_error) {
      Toast.show({
        type: 'error',
        text1: 'Error',
        text2: 'Failed to delete task',
      });
    }
  };

  const renderTaskForm = (): JSX.Element => (
    <Card>
      <Card.Title>New Task</Card.Title>
      <Input
        placeholder="Task Title"
        value={newTask.title}
        onChangeText={text => setNewTask(prev => ({ ...prev, title: text }))}
      />
      <Input
        placeholder="Description (optional)"
        multiline
        value={newTask.description}
        onChangeText={text => setNewTask(prev => ({ ...prev, description: text }))}
      />
      
      <Text>Difficulty Level (1-5)</Text>
      <Slider
        value={newTask.difficulty}
        onValueChange={value => setNewTask(prev => ({ ...prev, difficulty: value }))}
        minimumValue={1}
        maximumValue={5}
        step={1}
        thumbStyle={styles.sliderThumb}
      />
      
      <Text>Energy Required (1-10)</Text>
      <Slider
        value={newTask.energyRequired}
        onValueChange={value => setNewTask(prev => ({ ...prev, energyRequired: value }))}
        minimumValue={1}
        maximumValue={10}
        step={1}
        thumbStyle={styles.sliderThumb}
      />

      <Button
        title="Get AI Breakdown Suggestions"
        onPress={handleAddSubtask}
        type="outline"
        containerStyle={styles.button}
      />

      {aiSuggestions.length > 0 && (
        <Card>
          <Card.Title>Suggested Subtasks</Card.Title>
          <ScrollView style={styles.suggestionsContainer}>
            {aiSuggestions.map((suggestion, index) => (
              <Chip
                key={index}
                title={suggestion}
                onPress={() => addSubtaskFromSuggestion(suggestion)}
                type="outline"
                containerStyle={styles.chip}
              />
            ))}
          </ScrollView>
        </Card>
      )}

      <View style={styles.subtasksList}>
        <Text style={styles.subtitle}>Subtasks</Text>
        {newTask.subtasks?.map((subtask, index) => (
          <View key={index} style={styles.subtaskItem}>
            <Text>{subtask.title}</Text>
            <Input
              placeholder="Duration (minutes)"
              keyboardType="numeric"
              value={subtask.estimatedDuration.toString()}
              onChangeText={value => {
                const updatedSubtasks = [...(newTask.subtasks ?? [])];
                if (updatedSubtasks[index]) {
                  updatedSubtasks[index].estimatedDuration = parseInt(value) || 0;
                }
                setNewTask(prev => ({ ...prev, subtasks: updatedSubtasks }));
              }}
              containerStyle={styles.durationInput}
            />
          </View>
        ))}
      </View>

      <Button
        title="Save Task"
        onPress={async () => {
          if (_selectedTask) {
            await handleUpdateTask(_selectedTask.id, {
              title: newTask.title,
              description: newTask.description,
              startTime: newTask.startTime,
              endTime: newTask.endTime,
              difficulty: newTask.difficulty,
              energyRequired: newTask.energyRequired,
              subtasks: newTask.subtasks,
              reminders: newTask.reminders,
              recurring: newTask.recurring,
            });
          } else {
            await handleSaveTask();
          }
          setShowTaskForm(false);
        }}
        loading={loading}
        disabled={loading}
        containerStyle={styles.button}
      />
    </Card>
  );

  const renderTaskList = (): JSX.Element => (
    <ScrollView>
      {loading ? (
        <Card>
          <Card.Title>Loading tasks...</Card.Title>
          {/* You can add a more sophisticated loading skeleton here */}
        </Card>
      ) : tasks.length === 0 ? (
        <Card>
          <Card.Title>No Tasks</Card.Title>
          <Text>Click "Add New Task" to create your first task.</Text>
        </Card>
      ) : (
        tasks.map(task => (
          <Card key={task.id} containerStyle={{ borderLeftColor: task.color, borderLeftWidth: 5 }}>
            <View style={styles.taskHeader}>
              <Text style={styles.taskTitle}>{task.title}</Text>
              <View style={styles.taskActions}>
                <Button
                  icon={<Icon name="edit" size={20} />}
                  type="clear"
                  onPress={() => {
                    setSelectedTask(task);
                    setNewTask({
                      title: task.title,
                      description: task.description,
                      startTime: task.startTime,
                      endTime: task.endTime,
                      difficulty: task.difficulty,
                      energyRequired: task.energyRequired,
                      subtasks: task.subtasks,
                      reminders: task.reminders,
                      recurring: task.recurring,
                    });
                    setShowTaskForm(true);
                  }}
                />
                <Button
                  icon={<Icon name="delete" size={20} color="red" />}
                  type="clear"
                  onPress={() => handleDeleteTask(task.id)}
                  testID={`delete-task-${task.id}`}
                />
              </View>
            </View>
            
            <Text style={styles.taskTime}>
              {format(new Date(task.startTime), 'h:mm a')} - {format(new Date(task.endTime), 'h:mm a')}
            </Text>
            
            {task.subtasks.length > 0 && (
              <View style={styles.subtaskProgress}>
                <Text>Progress: {task.subtasks.filter(st => st.completed).length}/{task.subtasks.length}</Text>
                <View style={styles.progressBar}>
                  <View 
                    style={[
                      styles.progressFill,
                      { width: `${(task.subtasks.filter(st => st.completed).length / task.subtasks.length) * 100}%` }
                    ]} 
                  />
                </View>
              </View>
            )}
          </Card>
        ))
      )}
    </ScrollView>
  );

  return (
    <View style={styles.container}>
      <Button
        title={showTaskForm ? "View Tasks" : "Add New Task"}
        onPress={() => setShowTaskForm(!showTaskForm)}
        containerStyle={styles.button}
      />
      
      {showTaskForm ? renderTaskForm() : renderTaskList()}
    </View>
  );
}

const useStyles = makeStyles((theme) => ({
  container: {
    flex: 1,
    padding: 16,
  },
  button: {
    marginVertical: 8,
  },
  sliderThumb: {
    backgroundColor: theme.colors.primary,
  },
  suggestionsContainer: {
    maxHeight: 150,
  },
  chip: {
    margin: 4,
  },
  subtasksList: {
    marginVertical: 16,
  },
  subtitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  subtaskItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  durationInput: {
    width: 100,
  },
  taskHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  taskTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    flex: 1,
  },
  taskActions: {
    flexDirection: 'row',
    alignItems: 'center',
    marginLeft: 8,
  },
  taskMetrics: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 8,
  },
  taskTime: {
    color: theme.colors.grey3,
    marginVertical: 8,
  },
  subtaskProgress: {
    marginTop: 8,
  },
  progressBar: {
    height: 4,
    backgroundColor: theme.colors.grey5,
    borderRadius: 2,
    marginTop: 4,
  },
  progressFill: {
    height: '100%',
    backgroundColor: theme.colors.primary,
    borderRadius: 2,
  },
})); 