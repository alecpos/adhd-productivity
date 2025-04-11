import AsyncStorage from '@react-native-async-storage/async-storage';
import { renderHook, act } from '@testing-library/react-native';
import { Alert } from 'react-native';

import { api } from '@/lib/api';
import { createMockApiError } from '@/test-utils/error';
import { logger } from '@/utils/logger';

import { AuthProvider, useAuth } from '../AuthContext';

// Helper function to safely wrap act with proper types
const actSafe = async <T,>(callback: () => Promise<T>): Promise<T> => {
  let result: T;
  logger.debug('🔄 Starting actSafe execution');
  // eslint-disable-next-line @typescript-eslint/no-unsafe-call
  await act(async () => {
    result = await callback();
  });
  logger.debug('✅ Completed actSafe execution');
  return result!;
};

// Test logging utility
const logTest = (action: string, data?: Record<string, unknown>): void => {
  const logData = {
    action,
    ...(data && { data })
  };
  logger.debug('🧪 Test:', logData);
};

// Mock dependencies
jest.mock('@react-native-async-storage/async-storage', () => ({
  setItem: jest.fn(),
  getItem: jest.fn(),
  multiGet: jest.fn(),
  multiSet: jest.fn(),
  multiRemove: jest.fn(),
  removeItem: jest.fn(),
}));

jest.mock('expo-router', () => ({
  useRouter: () => ({
    replace: jest.fn(),
  }),
}));

jest.mock('react-native', () => ({
  Alert: {
    alert: jest.fn(),
  },
}));

// Mock the API singleton
jest.mock('@/lib/api');

describe('AuthContext', () => {
  const mockUser = {
    id: 'test-user-id',
    username: 'testuser',
    email: 'test@example.com',
    created_at: '2024-03-20T12:00:00Z',
    updated_at: '2024-03-20T12:00:00Z'
  };

  beforeEach(() => {
    logTest('beforeEach', { action: 'setup' });
    jest.clearAllMocks();
    // Reset API headers
    api.defaults.headers.Authorization = null;
    logTest('beforeEach', { action: 'complete', apiHeaders: api.defaults.headers });
  });

  afterEach(() => {
    logTest('afterEach', { action: 'cleanup' });
  });

  it('provides auth context with initial values', async () => {
    logTest('test_start', { name: 'provides auth context with initial values' });
    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });

    // Wait for initial auth check to complete
    await actSafe(async () => {
      await new Promise<void>(resolve => setTimeout(resolve, 0));
    });

    logTest('assertions', {
      user: result.current.user,
      loading: result.current.loading,
      error: result.current.error,
      isAuthenticated: result.current.isAuthenticated
    });

    expect(result.current.user).toBeNull();
    expect(result.current.loading).toBeFalsy();
    expect(result.current.error).toBeNull();
    expect(result.current.isAuthenticated).toBeFalsy();
    logTest('test_complete', { name: 'provides auth context with initial values' });
  });

  it('successfully logs in a user', async () => {
    logTest('test_start', { name: 'successfully logs in a user' });
    const mockLoginResponse = {
      data: {
        access_token: 'test-token',
        token_type: 'Bearer',
        user: mockUser,
      },
    };

    logTest('setup_mocks', {
      mockLoginResponse,
      apiPostMock: 'configured',
      asyncStorageMock: 'configured'
    });

    (api.post as jest.Mock).mockResolvedValueOnce(mockLoginResponse);
    (AsyncStorage.multiSet as jest.Mock).mockResolvedValueOnce(null);

    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });

    await actSafe(async () => {
      logTest('login_attempt', { email: 'test@example.com' });
      await result.current.login('test@example.com', 'password');
    });

    logTest('verify_api_calls', {
      apiPostCalled: (api.post as jest.Mock).mock.calls.length,
      asyncStorageMultiSetCalled: (AsyncStorage.multiSet as jest.Mock).mock.calls.length,
      apiHeaders: api.defaults.headers
    });

    expect(api.post).toHaveBeenCalledWith('/api/auth/login', {
      username: 'test@example.com',
      password: 'password',
    });
    expect(AsyncStorage.multiSet).toHaveBeenCalledWith([
      ['auth_token', 'test-token'],
      ['user', JSON.stringify(mockUser)],
    ]);
    expect(api.defaults.headers.Authorization).toBe('Bearer test-token');
    expect(result.current.user).toStrictEqual(mockUser);
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();

    logTest('test_complete', {
      name: 'successfully logs in a user',
      finalState: {
        user: result.current.user,
        isAuthenticated: result.current.isAuthenticated,
        loading: result.current.loading,
        error: result.current.error
      }
    });
  });

  it('handles login errors', async () => {
    const errorMessage = 'Invalid credentials';
    const mockError = createMockApiError(401, errorMessage);
    (api.post as jest.Mock).mockRejectedValueOnce(mockError);

    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });

    let error: unknown;
    await actSafe(async () => {
      try {
        await result.current.login('test@example.com', 'wrong-password');
      } catch (err) {
        error = err;
      }
    });

    expect(error).toBeDefined();
    expect(error).toBeInstanceOf(Error);
    expect((error as Error).message).toBe(errorMessage);
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBeNull();
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBe(errorMessage);
    expect(Alert.alert).toHaveBeenCalledWith('Login Failed', errorMessage);
  });

  it('successfully registers a new user', async () => {
    const mockRegisterResponse = {
      data: {
        access_token: 'test-token',
        token_type: 'Bearer',
        user: mockUser,
      },
    };

    (api.post as jest.Mock).mockResolvedValueOnce(mockRegisterResponse);
    (AsyncStorage.multiSet as jest.Mock).mockResolvedValueOnce(null);

    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });

    await actSafe(async () => {
      await result.current.register('testuser', 'test@example.com', 'password');
    });

    expect(api.post).toHaveBeenCalledWith('/api/auth/register', {
      username: 'testuser',
      email: 'test@example.com',
      password: 'password',
    });
    expect(AsyncStorage.multiSet).toHaveBeenCalledWith([
      ['auth_token', 'test-token'],
      ['user', JSON.stringify(mockUser)],
    ]);
    expect(api.defaults.headers.Authorization).toBe('Bearer test-token');
    expect(result.current.user).toStrictEqual(mockUser);
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('handles registration errors', async () => {
    const errorMessage = 'Email already exists';
    const mockError = createMockApiError(400, errorMessage);
    (api.post as jest.Mock).mockRejectedValueOnce(mockError);

    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });

    let error: unknown;
    await actSafe(async () => {
      try {
        await result.current.register('testuser', 'test@example.com', 'password');
      } catch (err) {
        error = err;
      }
    });

    expect(error).toBeDefined();
    expect(error).toBeInstanceOf(Error);
    expect((error as Error).message).toBe(errorMessage);
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBeNull();
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBe(errorMessage);
    expect(Alert.alert).toHaveBeenCalledWith('Registration Failed', errorMessage);
  });

  it('successfully logs out a user', async () => {
    // Setup initial authenticated state
    const mockLoginResponse = {
      data: {
        access_token: 'test-token',
        token_type: 'Bearer',
        user: mockUser,
      },
    };
    (api.post as jest.Mock).mockResolvedValueOnce(mockLoginResponse);
    (AsyncStorage.multiSet as jest.Mock).mockResolvedValueOnce(null);
    (AsyncStorage.multiRemove as jest.Mock).mockResolvedValueOnce(null);

    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });

    // First login
    await actSafe(async () => {
      await result.current.login('test@example.com', 'password');
    });

    // Then logout
    (api.post as jest.Mock).mockResolvedValueOnce({});
    await actSafe(async () => {
      await result.current.logout();
    });

    expect(api.post).toHaveBeenCalledWith('/api/auth/logout');
    expect(AsyncStorage.multiRemove).toHaveBeenCalledWith(['auth_token', 'user']);
    expect(api.defaults.headers.Authorization).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBeNull();
  });

  it('checks auth status with valid token', async () => {
    const mockMeResponse = {
      data: {
        data: mockUser,
      },
    };

    (AsyncStorage.getItem as jest.Mock).mockResolvedValueOnce('test-token');
    (api.get as jest.Mock).mockResolvedValueOnce(mockMeResponse);

    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });

    await actSafe(async () => {
      await result.current.checkAuthStatus();
    });

    expect(api.defaults.headers.Authorization).toBe('Bearer test-token');
    expect(result.current.user).toStrictEqual(mockUser);
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('checks auth status with invalid token', async () => {
    const errorMessage = 'Invalid token';
    const mockError = createMockApiError(401, errorMessage);

    (AsyncStorage.getItem as jest.Mock).mockResolvedValueOnce('invalid-token');
    (api.get as jest.Mock).mockRejectedValueOnce(mockError);
    (AsyncStorage.multiRemove as jest.Mock).mockResolvedValueOnce(null);

    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });

    await actSafe(async () => {
      await result.current.checkAuthStatus();
    });

    expect(AsyncStorage.multiRemove).toHaveBeenCalledWith(['auth_token', 'user']);
    expect(api.defaults.headers.Authorization).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBeNull();
    expect(result.current.loading).toBe(false);
  });

  it('clears error state', async () => {
    const errorMessage = 'Invalid credentials';
    const mockError = createMockApiError(401, errorMessage);
    (api.post as jest.Mock).mockRejectedValueOnce(mockError);

    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });

    // First trigger an error
    await actSafe(async () => {
      try {
        await result.current.login('test@example.com', 'wrong-password');
        fail('Expected login to fail');
      } catch (_err) {
        // Expected error
      }
    });

    expect(result.current.error).toBe(errorMessage);

    // Then clear it
    await actSafe(async () => {
      result.current.clearError();
    });

    expect(result.current.error).toBeNull();
  });

  it('throws error when used outside provider', () => {
    const consoleError = jest.spyOn(console, 'error').mockImplementation(() => {});
    expect(() => {
      const { result } = renderHook(() => useAuth());
      return result.current;
    }).toThrow('useAuth must be used within an AuthProvider');
    consoleError.mockRestore();
  });
});
