import taskReducer, {
  addTask,
  updateTask,
  deleteTask,
  setLoading,
  setError
} from '../taskSlice';

import type {
  TaskState,
  Task
} from '../taskSlice';

describe('taskSlice', () => {
  let initialState: TaskState;

  beforeEach(() => {
    initialState = {
      tasks: [],
      loading: false,
      error: null
    };
  });

  it('should handle initial state', () => {
    expect(taskReducer(undefined, { type: 'unknown' })).toEqual({
      tasks: [],
      loading: false,
      error: null
    });
  });

  it('should handle addTask', () => {
    const task: Task = {
      id: '1',
      title: 'Test Task',
      description: 'Test Description',
      startTime: new Date().toISOString(),
      endTime: new Date().toISOString(),
      difficulty: 1,
      energyRequired: 1,
      subtasks: [],
      completed: false,
      reminders: [],
      userId: 'test-user'
    };

    const actual = taskReducer(initialState, addTask(task));
    expect(actual.tasks).toHaveLength(1);
    expect(actual.tasks[0]).toEqual(task);
  });

  it('should handle updateTask', () => {
    const task: Task = {
      id: '1',
      title: 'Test Task',
      description: 'Test Description',
      startTime: new Date().toISOString(),
      endTime: new Date().toISOString(),
      difficulty: 1,
      energyRequired: 1,
      subtasks: [],
      completed: false,
      reminders: [],
      userId: 'test-user'
    };

    const updatedTask: Task = {
      ...task,
      title: 'Updated Task'
    };

    let state = taskReducer(initialState, addTask(task));
    state = taskReducer(state, updateTask(updatedTask));

    expect(state.tasks).toHaveLength(1);
    expect(state.tasks[0].title).toBe('Updated Task');
  });

  it('should handle deleteTask', () => {
    const task: Task = {
      id: '1',
      title: 'Test Task',
      description: 'Test Description',
      startTime: new Date().toISOString(),
      endTime: new Date().toISOString(),
      difficulty: 1,
      energyRequired: 1,
      subtasks: [],
      completed: false,
      reminders: [],
      userId: 'test-user'
    };

    let state = taskReducer(initialState, addTask(task));
    state = taskReducer(state, deleteTask(task.id));

    expect(state.tasks).toHaveLength(0);
  });

  it('should handle setLoading', () => {
    const actual = taskReducer(initialState, setLoading(true));
    expect(actual.loading).toBe(true);
  });

  it('should handle setError', () => {
    const errorMessage = 'Test error';
    const actual = taskReducer(initialState, setError(errorMessage));
    expect(actual.error).toBe(errorMessage);
  });
});
