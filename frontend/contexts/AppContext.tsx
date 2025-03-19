import type { ReactNode } from "react";
import React, { createContext, useContext, useReducer, useEffect } from "react";

import axios from "axios";

// Types
type Task = {
  id: string;
  title: string;
  description: string;
  due_date: string;
  recurring?: string;
};

type Insights = {
  total_tasks: number;
  completed_tasks: number;
  completion_rate: number;
};

type HyperfocusState = {
  sessionActive: boolean;
  streaks: {
    current_streak: number;
    highest_streak: number;
    badges: string[];
  };
};

type AppState = {
  tasks: Task[];
  insights: Insights;
  hyperfocus: HyperfocusState;
};

type Action =
  | { type: "SET_TASKS"; payload: Task[] }
  | { type: "SET_INSIGHTS"; payload: Insights }
  | { type: "SET_HYPERFOCUS"; payload: Partial<HyperfocusState> };

// Initial State
const initialState: AppState = {
  tasks: [],
  insights: { total_tasks: 0, completed_tasks: 0, completion_rate: 0 },
  hyperfocus: { sessionActive: false, streaks: { current_streak: 0, highest_streak: 0, badges: [] } },
};

// Reducer
function appReducer(state: AppState, action: Action): AppState {
  switch (action.type) {
    case "SET_TASKS":
      return { ...state, tasks: action.payload };
    case "SET_INSIGHTS":
      return { ...state, insights: action.payload };
    case "SET_HYPERFOCUS":
      return { ...state, hyperfocus: { ...state.hyperfocus, ...action.payload } };
    default:
      return state;
  }
}

// Context
const AppContext = createContext<{ state: AppState; dispatch: React.Dispatch<Action> } | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [tasksResponse, insightsResponse, streaksResponse] = await Promise.all([
          axios.get("http://localhost:8000/tasks"),
          axios.get("http://localhost:8000/tasks/insights"),
          axios.get("http://localhost:8000/hyperfocus/streaks"),
        ]);
        dispatch({ type: "SET_TASKS", payload: tasksResponse.data });
        dispatch({ type: "SET_INSIGHTS", payload: insightsResponse.data });
        dispatch({ type: "SET_HYPERFOCUS", payload: { streaks: streaksResponse.data.streaks } });
      } catch (error) {
        console.error("Error loading initial data:", error);
      }
    };
    fetchData();
  }, []);

  return <AppContext.Provider value={{ state, dispatch }}>{children}</AppContext.Provider>;
}

export const useAppContext = () => {
  const context = useContext(AppContext);
  if (!context) throw new Error("useAppContext must be used within an AppProvider");
  return context;
};
