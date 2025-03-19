import React from 'react';

import { renderHook, act } from '@testing-library/react-native';

import { MentalHealthService } from '@/app/services/mental-health';

import { useAuth } from '../AuthContext';
import { MentalHealthProvider, useMentalHealth, MoodLevel, StressLevel } from '../MentalHealthContext';

// Mock the AuthContext
jest.mock('../AuthContext', () => ({
  useAuth: jest.fn()
}));

// Mock the MentalHealthService
jest.mock('@/app/services/mental-health', () => ({
  MentalHealthService: jest.fn()
}));

describe('MentalHealthContext', () => {
  const mockUser = { id: 'test-user-id' };
  const mockStats = {
    mood_average: 3.5,
    stress_level_average: 2,
    anxiety_level_average: 1,
    energy_level_average: 4,
    focus_level_average: 3,
    sleep_hours_average: 7.5,
    sleep_quality_average: 4,
    total_logs: 10,
    recent_moods: [
      { date: '2024-03-20', mood: 4, notes: 'Good day' }
    ],
    streak: 5,
    most_common_activities: ['Exercise', 'Reading'],
    most_common_triggers: ['Deadlines', 'Meetings'],
    most_common_coping_strategies: ['Deep breathing', 'Walking'],
    updated_at: '2024-03-20T12:00:00Z'
  };

  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();
    
    // Setup auth mock
    (useAuth as jest.Mock).mockReturnValue({ user: mockUser });
    
    // Setup service mock with direct mock functions
    const mockCreateLog = jest.fn().mockResolvedValue({ success: true });
    const mockGetUserStats = jest.fn().mockResolvedValue(mockStats);
    
    (MentalHealthService as jest.Mock).mockImplementation(() => ({
      createLog: mockCreateLog,
      getUserStats: mockGetUserStats
    }));
  });

  it('provides mental health context with initial values', () => {
    const { result } = renderHook(() => useMentalHealth(), {
      wrapper: MentalHealthProvider
    });

    expect(result.current.stats).toBeNull();
    expect(result.current.loading).toBeFalsy();
    expect(result.current.error).toBeNull();
    expect(typeof result.current.createLog).toBe('function');
    expect(typeof result.current.getStats).toBe('function');
  });

  it('successfully creates a mental health log', async () => {
    const { result } = renderHook(() => useMentalHealth(), {
      wrapper: MentalHealthProvider
    });

    const logData = {
      moodScore: MoodLevel.High,
      stressLevel: StressLevel.Low,
      notes: 'Test note'
    };

    await act(async () => {
      await result.current.createLog(logData);
    });

    // Get the mock instance and its createLog method
    const mockServiceInstance = (MentalHealthService as jest.Mock).mock.results[0].value;
    
    expect(mockServiceInstance.createLog).toHaveBeenCalledWith({
      userId: mockUser.id,
      mood: String(logData.moodScore),
      intensity: logData.stressLevel,
      note: logData.notes,
      triggers: [],
      timestamp: expect.any(String)
    });
  });

  it('successfully fetches user stats', async () => {
    const { result } = renderHook(() => useMentalHealth(), {
      wrapper: MentalHealthProvider
    });

    await act(async () => {
      await result.current.getStats();
    });

    expect(result.current.stats).toEqual(mockStats);
    expect(result.current.loading).toBeFalsy();
    expect(result.current.error).toBeNull();

    // Get the mock instance and its getUserStats method
    const mockServiceInstance = (MentalHealthService as jest.Mock).mock.results[0].value;
    expect(mockServiceInstance.getUserStats).toHaveBeenCalled();
  });

  it('handles errors when creating log', async () => {
    const mockError = new Error('Failed to create log');
    const mockCreateLog = jest.fn().mockRejectedValue(mockError);
    
    (MentalHealthService as jest.Mock).mockImplementation(() => ({
      createLog: mockCreateLog,
      getUserStats: jest.fn()
    }));

    const { result } = renderHook(() => useMentalHealth(), {
      wrapper: MentalHealthProvider
    });

    const logData = {
      moodScore: MoodLevel.High,
      stressLevel: StressLevel.Low,
      notes: 'Test note'
    };

    await expect(result.current.createLog(logData)).rejects.toThrow(mockError);
  });

  it('handles errors when fetching stats', async () => {
    const mockError = new Error('Failed to fetch stats');
    const mockGetUserStats = jest.fn().mockRejectedValue(mockError);
    
    (MentalHealthService as jest.Mock).mockImplementation(() => ({
      createLog: jest.fn(),
      getUserStats: mockGetUserStats
    }));

    const { result } = renderHook(() => useMentalHealth(), {
      wrapper: MentalHealthProvider
    });

    await act(async () => {
      try {
        await result.current.getStats();
      } catch (error) {
        // Error is expected
      }
    });

    expect(result.current.error).toBe(mockError.message);
    expect(result.current.loading).toBeFalsy();
  });

  it('throws error when used outside provider', () => {
    expect(() => {
      renderHook(() => useMentalHealth());
    }).toThrow('useMentalHealth must be used within a MentalHealthProvider');
  });
}); 