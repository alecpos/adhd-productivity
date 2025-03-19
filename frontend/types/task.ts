export enum TaskStatus {
  TODO = 'todo',
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled',
  MISSED = 'missed',
  BLOCKED = 'blocked'
}

export enum TaskPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  URGENT = 'urgent'
}

export interface Task {
  /** Unique identifier for the task */
  id: string;
  /** ID of the user who owns this task */
  user_id: string;
  /** Title/name of the task */
  title: string;
  /** Optional detailed description of the task */
  description?: string;
  /** Current status of the task */
  status: TaskStatus;
  /** Priority level of the task */
  priority: TaskPriority;
  /** Optional due date for the task */
  due_date?: string;
  /** Estimated time to complete the task (in minutes) */
  estimated_duration?: number;
  /** Actual time taken to complete the task (in minutes) */
  actual_duration?: number;
  /** Date when the task was completed */
  completion_date?: string;
  /** Whether the task has been completed */
  completed: boolean;
  /** Energy level required to complete the task (1-10) */
  energy_required?: number;
  /** Quality score of the completed task (1-10) */
  quality_score?: number;
  /** Percentage of task completion (0-100) */
  completion_rate?: number;
  /** User-rated difficulty of the task (1-10) */
  difficulty_rating?: number;
  /** Additional metadata for the task */
  meta_data?: Record<string, unknown>;
  /** Optional category/tag for the task */
  category?: string;
}

export interface TaskStats {
  total_tasks: number;
  completed_tasks: number;
  pending_tasks: number;
  completion_rate: number;
  average_duration?: number;
  average_quality?: number;
  most_productive_category?: string;
} 