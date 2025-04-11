import { renderHook, act } from '@testing-library/react-hooks';
import { useTaskState } from '../useTaskState';
import { TaskStatus, TaskPriority } from '../../types/task';
import { api } from '../../services/api';

// Mock the API service
jest.mock('../../services/api');

describe('useTaskState', () => {
  const mockTask = {
    id: '1',
    user_id: 'user1',
    title: 'Test Task',
    status: TaskStatus.TODO,
    priority: TaskPriority.MEDIUM,
    completed: false,
    next_states: [TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED, TaskStatus.BLOCKED]
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should initialize with the provided task', () => {
    const { result } = renderHook(() => useTaskState(mockTask));

    expect(result.current.currentTask).toEqual(mockTask);
    expect(result.current.isUpdating).toBe(false);
    expect(result.current.error).toBe(null);
  });

  it('should return valid next states', () => {
    const { result } = renderHook(() => useTaskState(mockTask));

    expect(result.current.getNextStates()).toEqual([
      TaskStatus.IN_PROGRESS,
      TaskStatus.CANCELLED,
      TaskStatus.BLOCKED
    ]);
  });

  it('should correctly check if a transition is valid', () => {
    const { result } = renderHook(() => useTaskState(mockTask));

    expect(result.current.canTransitionTo(TaskStatus.IN_PROGRESS)).toBe(true);
    expect(result.current.canTransitionTo(TaskStatus.COMPLETED)).toBe(false);
  });

  it('should successfully update task status', async () => {
    const updatedTask = {
      ...mockTask,
      status: TaskStatus.IN_PROGRESS,
      next_states: [TaskStatus.COMPLETED, TaskStatus.CANCELLED, TaskStatus.BLOCKED]
    };

    (api.patch as jest.Mock).mockResolvedValueOnce({ data: updatedTask });

    const { result } = renderHook(() => useTaskState(mockTask));

    await act(async () => {
      const success = await result.current.updateTaskStatus(TaskStatus.IN_PROGRESS);
      expect(success).toBe(true);
    });

    expect(result.current.currentTask).toEqual(updatedTask);
    expect(result.current.isUpdating).toBe(false);
    expect(result.current.error).toBe(null);
    expect(api.patch).toHaveBeenCalledWith('/tasks/1/status', {
      status: TaskStatus.IN_PROGRESS
    });
  });

  it('should prevent invalid state transitions', async () => {
    const { result } = renderHook(() => useTaskState(mockTask));

    await act(async () => {
      const success = await result.current.updateTaskStatus(TaskStatus.COMPLETED);
      expect(success).toBe(false);
    });

    expect(result.current.currentTask).toEqual(mockTask);
    expect(result.current.error).toBe(
      `Invalid state transition from ${TaskStatus.TODO} to ${TaskStatus.COMPLETED}`
    );
    expect(api.patch).not.toHaveBeenCalled();
  });

  it('should handle API errors during status update', async () => {
    const errorMessage = 'API Error';
    (api.patch as jest.Mock).mockRejectedValueOnce(new Error(errorMessage));

    const { result } = renderHook(() => useTaskState(mockTask));

    await act(async () => {
      const success = await result.current.updateTaskStatus(TaskStatus.IN_PROGRESS);
      expect(success).toBe(false);
    });

    expect(result.current.currentTask).toEqual(mockTask);
    expect(result.current.isUpdating).toBe(false);
    expect(result.current.error).toBe(errorMessage);
  });

  it('should handle non-Error API errors', async () => {
    (api.patch as jest.Mock).mockRejectedValueOnce('String error');

    const { result } = renderHook(() => useTaskState(mockTask));

    await act(async () => {
      const success = await result.current.updateTaskStatus(TaskStatus.IN_PROGRESS);
      expect(success).toBe(false);
    });

    expect(result.current.currentTask).toEqual(mockTask);
    expect(result.current.isUpdating).toBe(false);
    expect(result.current.error).toBe('Failed to update task status');
  });
}); 