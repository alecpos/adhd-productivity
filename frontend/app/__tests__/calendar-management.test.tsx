import React from 'react';

import { configureStore } from '@reduxjs/toolkit';
import { render, fireEvent, act } from '@testing-library/react-native';
import { View, Text as RNText } from 'react-native';
import { Provider } from 'react-redux';


import CalendarManagement from '../(auth)/calendar-management';
import taskReducer from '../store/slices/taskSlice';

import type { Task, TaskState } from '../store/slices/taskSlice';
import type { Store } from '@reduxjs/toolkit';

// Mock @rneui/themed components
jest.mock('@rneui/themed', () => {
  const React = require('react');
  const { View, Text } = require('react-native');

  const mockComponent = (name: string) => {
    const Component = ({ children, testID, onPress, style, ...props }: any) => (
      <View testID={testID} style={style}>
        {typeof children === 'string' ? <Text>{children}</Text> : children}
      </View>
    );
    Component.displayName = name;
    return Component;
  };

  type CardComponent = ReturnType<typeof mockComponent> & {
    Title: ReturnType<typeof mockComponent>;
  };

  const Card = mockComponent('Card') as CardComponent;
  Card.Title = mockComponent('CardTitle');

  return {
    Text: mockComponent('Text'),
    Button: mockComponent('Button'),
    Card,
    Input: mockComponent('Input'),
    Slider: mockComponent('Slider'),
    Chip: mockComponent('Chip'),
    Icon: mockComponent('Icon'),
    makeStyles: () => ({
      container: {},
      button: {},
      sliderThumb: {},
      suggestionsContainer: {},
      chip: {},
      subtasksList: {},
      subtitle: {},
      subtaskItem: {},
      durationInput: {},
      taskHeader: {},
      taskTitle: {},
      taskActions: {},
      taskMetrics: {},
      taskTime: {},
      subtaskProgress: {},
      progressBar: {},
      progressFill: {},
    }),
    useTheme: () => ({
      theme: {
        colors: {
          primary: '#2089dc',
          secondary: '#ca71eb',
          success: '#52c41a',
          error: '#ff190c',
          grey3: '#86939e',
          grey5: '#e1e8ee',
        },
      },
    }),
  };
});

// Mock useAuth hook
jest.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { id: 'test-user', email: 'test@example.com' },
    loading: false
  })
}));

interface RootState {
  tasks: TaskState;
}

// Mock TaskService
jest.mock('@/app/services/task', () => ({
  TaskService: jest.fn().mockImplementation(() => ({
    getTasks: jest.fn().mockResolvedValue([]),
    createTask: jest.fn().mockImplementation(task => Promise.resolve({ ...task, id: '1' })),
    updateTask: jest.fn().mockImplementation((id, task) => Promise.resolve({ ...task, id })),
    deleteTask: jest.fn().mockResolvedValue(true)
  }))
}));

// Mock huggingface service
jest.mock('@/app/services/huggingface', () => ({
  __esModule: true,
  default: {
    getTaskBreakdown: jest.fn().mockResolvedValue(['Subtask 1', 'Subtask 2'])
  }
}));

// Mock Toast
jest.mock('react-native-toast-message', () => ({
  show: jest.fn()
}));

// Create a mock store
const createTestStore = (): Store<RootState> => {
  return configureStore({
    reducer: {
      tasks: taskReducer
    }
  });
};

describe('CalendarManagement', () => {
  let store: Store<RootState>;

  beforeEach(() => {
    store = createTestStore();
    jest.clearAllMocks();
  });

  it('renders calendar component', () => {
    const { getByTestId } = render(
      <Provider store={store}>
        <CalendarManagement />
      </Provider>
    );
    expect(getByTestId('calendar-view')).toBeTruthy();
  });

  it('opens task input modal when add button is pressed', () => {
    const { getByTestId } = render(
      <Provider store={store}>
        <CalendarManagement />
      </Provider>
    );

    const addButton = getByTestId('add-task-button');
    fireEvent.press(addButton);

    expect(getByTestId('task-input-modal')).toBeTruthy();
  });

  it('creates a new task when form is submitted', async () => {
    const { getByTestId, getByPlaceholderText } = render(
      <Provider store={store}>
        <CalendarManagement />
      </Provider>
    );

    // Open modal
    fireEvent.press(getByTestId('add-task-button'));

    // Fill form
    fireEvent.changeText(getByPlaceholderText('Task Title'), 'Test Task');
    fireEvent.changeText(getByPlaceholderText('Description'), 'Test Description');

    // Submit form
    await act(async () => {
      fireEvent.press(getByTestId('submit-task-button'));
    });

    // Verify task was added to store
    const state = store.getState();
    expect(state.tasks.tasks).toContainEqual(
      expect.objectContaining({
        title: 'Test Task',
        description: 'Test Description',
        startTime: expect.any(String),
        endTime: expect.any(String),
        difficulty: expect.any(Number),
        energyRequired: expect.any(Number),
        subtasks: expect.any(Array),
        completed: expect.any(Boolean),
        reminders: expect.any(Array),
        userId: expect.any(String)
      })
    );
  });

  it('updates task when edit is submitted', async () => {
    const initialTask: Task = {
      id: '1',
      title: 'Initial Task',
      description: 'Initial Description',
      startTime: new Date().toISOString(),
      endTime: new Date().toISOString(),
      difficulty: 1,
      energyRequired: 1,
      subtasks: [],
      completed: false,
      reminders: [],
      userId: 'test-user'
    };

    store = createTestStore();
    store.dispatch({ type: 'tasks/addTask', payload: initialTask });

    const { getByTestId, getByPlaceholderText } = render(
      <Provider store={store}>
        <CalendarManagement />
      </Provider>
    );

    // Open edit modal
    fireEvent.press(getByTestId(`edit-task-${initialTask.id}`));

    // Update form
    fireEvent.changeText(getByPlaceholderText('Task Title'), 'Updated Task');

    // Submit form
    await act(async () => {
      fireEvent.press(getByTestId('submit-task-button'));
    });

    // Verify task was updated in store
    const state = store.getState();
    expect(state.tasks.tasks).toContainEqual(
      expect.objectContaining({
        id: '1',
        title: 'Updated Task',
        startTime: expect.any(String),
        endTime: expect.any(String),
        difficulty: expect.any(Number),
        energyRequired: expect.any(Number),
        subtasks: expect.any(Array),
        completed: expect.any(Boolean),
        reminders: expect.any(Array),
        userId: expect.any(String)
      })
    );
  });

  it('deletes task when delete button is pressed', async () => {
    const taskToDelete: Task = {
      id: '1',
      title: 'Task to Delete',
      description: 'Will be deleted',
      startTime: new Date().toISOString(),
      endTime: new Date().toISOString(),
      difficulty: 1,
      energyRequired: 1,
      subtasks: [],
      completed: false,
      reminders: [],
      userId: 'test-user'
    };

    store = createTestStore();
    store.dispatch({ type: 'tasks/addTask', payload: taskToDelete });

    const { getByTestId } = render(
      <Provider store={store}>
        <CalendarManagement />
      </Provider>
    );

    // Delete task
    await act(async () => {
      fireEvent.press(getByTestId(`delete-task-${taskToDelete.id}`));
    });

    // Verify task was removed from store
    const state = store.getState();
    expect(state.tasks.tasks).not.toContainEqual(
      expect.objectContaining({
        id: taskToDelete.id,
        startTime: expect.any(String),
        endTime: expect.any(String),
        difficulty: expect.any(Number),
        energyRequired: expect.any(Number),
        subtasks: expect.any(Array),
        completed: expect.any(Boolean),
        reminders: expect.any(Array),
        userId: expect.any(String)
      })
    );
  });
});
