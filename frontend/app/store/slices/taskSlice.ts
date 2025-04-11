import { createSlice } from '@reduxjs/toolkit';

import type { PayloadAction } from '@reduxjs/toolkit';

export interface SubTask {
  id: string;
  title: string;
  completed: boolean;
  estimatedDuration: number;
}

export interface Task {
  id: string;
  title: string;
  description?: string;
  startTime: string;
  endTime: string;
  difficulty: number;
  energyRequired: number;
  subtasks: SubTask[];
  completed: boolean;
  recurring?: boolean;
  reminders: string[];
  color?: string;
  userId: string;
}

export interface TaskState {
  tasks: Task[];
  loading: boolean;
  error: string | null;
}

const initialState: TaskState = {
  tasks: [],
  loading: false,
  error: null
};

const taskSlice = createSlice({
  name: 'tasks',
  initialState,
  reducers: {
    addTask: (state: TaskState, action: PayloadAction<Task>) => {
      state.tasks.push(action.payload);
    },
    updateTask: (state: TaskState, action: PayloadAction<Task>) => {
      const index = state.tasks.findIndex(task => task.id === action.payload.id);
      if (index !== -1) {
        state.tasks[index] = action.payload;
      }
    },
    deleteTask: (state: TaskState, action: PayloadAction<string>) => {
      state.tasks = state.tasks.filter(task => task.id !== action.payload);
    },
    setTasks: (state: TaskState, action: PayloadAction<Task[]>) => {
      state.tasks = action.payload;
    },
    setLoading: (state: TaskState, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    setError: (state: TaskState, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    }
  }
});

export const { addTask, updateTask, deleteTask, setTasks, setLoading, setError } = taskSlice.actions;
export default taskSlice.reducer;
