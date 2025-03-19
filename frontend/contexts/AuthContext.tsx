import React, { createContext, useContext, useState, useEffect } from 'react';

import AsyncStorage from '@react-native-async-storage/async-storage';
import { useRouter } from 'expo-router';
import { Alert } from 'react-native';

import { api, setAuthErrorHandler } from '@/lib/api';
import { logger } from '@/utils/logger';

interface User {
  id: string;
  username: string;
  email: string;
  created_at: string;
  updated_at: string;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  isAuthenticated: boolean;
  isInitialized: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  checkAuthStatus: () => Promise<void>;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Logging utility
const logAuth = (action: string, data?: Record<string, unknown>): void => {
  const timestamp = new Date().toISOString();
  const logData = {
    timestamp,
    action,
    ...(data !== undefined && { data: typeof data === 'object' ? JSON.stringify(data) : data })
  };
  logger.debug('🔐 Auth:', logData);
};

export function AuthProvider({ children }: { children: React.ReactNode }): JSX.Element {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);
  const router = useRouter();

  const clearError = (): void => {
    logAuth('clear_error');
    setError(null);
  };

  // Log state changes
  useEffect(() => {
    logAuth('state_change', {
      isAuthenticated: !!user,
      isInitialized,
      loading,
      hasError: !!error,
      userId: user?.id
    });
  }, [user, loading, error, isInitialized]);

  // Set up auth error handler
  useEffect(() => {
    logAuth('setup_error_handler');
    const handler = (): void => {
      void (async (): Promise<void> => {
        logAuth('auth_error_handler_triggered');
        await AsyncStorage.multiRemove(['auth_token', 'user']);
        delete api.defaults.headers.Authorization;
        setUser(null);
      })();
    };
    setAuthErrorHandler(handler);
  }, []);

  const checkAuthStatus = async (): Promise<void> => {
    logAuth('check_auth_status_start');
    try {
      setLoading(true);
      const token = await AsyncStorage.getItem('auth_token');
      
      logAuth('token_check', { hasToken: token !== null });
      
      if (token === null) {
        setUser(null);
        logAuth('no_token_found');
      } else {
        // Set the token in the API client
        api.defaults.headers.Authorization = `Bearer ${token}`;
        logAuth('token_set_in_headers');

        const response = await api.get<{ data: User }>('/api/auth/me');
        logAuth('user_verified', { userId: response.data.data.id });
        setUser(response.data.data);
      }
    } catch (authError) {
      if (authError instanceof Error) {
        logAuth('check_auth_status_error', {
          message: authError.message,
          status: (authError as { response?: { status?: number } }).response?.status,
          detail: (authError as { response?: { data?: { detail?: string } } }).response?.data?.detail
        });
        logger.error('Error checking auth status:', authError);
      }
      await AsyncStorage.multiRemove(['auth_token', 'user']);
      delete api.defaults.headers.Authorization;
      setUser(null);
    } finally {
      setLoading(false);
      setIsInitialized(true);
      logAuth('check_auth_status_complete');
    }
  };

  // Handle navigation after initialization
  useEffect(() => {
    if (isInitialized && !loading) {
      if (!user) {
        logAuth('redirecting_to_login');
        router.replace('/(unauth)/login');
      } else {
        logAuth('redirecting_to_app');
        router.replace('/(auth)');
      }
    }
  }, [isInitialized, loading, user, router]);

  const login = async (email: string, password: string): Promise<void> => {
    logAuth('login_attempt', { email });
    setLoading(true);
    setError(null);
    try {
      const response = await api.post<AuthResponse>('/api/auth/login', {
        username: email,
        password,
      });

      const { access_token: token, user: userData } = response.data;
      logAuth('login_success', { userId: userData.id });

      // Store auth data
      await AsyncStorage.multiSet([
        ['auth_token', token],
        ['user', JSON.stringify(userData)]
      ]);

      // Update API client
      api.defaults.headers.Authorization = `Bearer ${token}`;
      
      // Update state
      setUser(userData);
      logAuth('login_complete', { userId: userData.id });
    } catch (err) {
      if (err instanceof Error) {
        const axiosError = err as { response?: { data?: { detail?: string }, status?: number } };
        const errorDetail = axiosError.response?.data?.detail;
        const message = errorDetail ?? 'Failed to login';
        logAuth('login_error', {
          message: err.message,
          status: axiosError.response?.status,
          detail: errorDetail,
        });
        setError(message);
        Alert.alert('Login Failed', message);
        throw new Error(message);
      }
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = async (): Promise<void> => {
    logAuth('logout_start', { userId: user?.id });
    setLoading(true);
    try {
      await api.post('/api/auth/logout');
      logAuth('logout_api_success');
    } catch (err) {
      if (err instanceof Error) {
        const axiosError = err as { response?: { status?: number } };
        logAuth('logout_api_error', {
          message: err.message,
          status: axiosError.response?.status
        });
        logger.error('Error during logout:', err);
      }
    } finally {
      await AsyncStorage.multiRemove(['auth_token', 'user']);
      delete api.defaults.headers.Authorization;
      setUser(null);
      setLoading(false);
      logAuth('logout_complete');
    }
  };

  const register = async (username: string, email: string, password: string): Promise<void> => {
    logAuth('register_start', { username, email });
    setLoading(true);
    setError(null);
    try {
      const response = await api.post<AuthResponse>('/api/auth/register', {
        username,
        email,
        password,
      });
      
      const { access_token: token, user: userData } = response.data;
      logAuth('register_success', { userId: userData.id });
      
      // Store auth data
      await AsyncStorage.multiSet([
        ['auth_token', token],
        ['user', JSON.stringify(userData)]
      ]);

      // Update API client
      api.defaults.headers.Authorization = `Bearer ${token}`;
      
      // Update state
      setUser(userData);
      logAuth('register_complete', { userId: userData.id });
    } catch (err) {
      if (err instanceof Error) {
        const axiosError = err as { response?: { data?: { detail?: string }, status?: number } };
        const errorDetail = axiosError.response?.data?.detail;
        const message = errorDetail ?? 'Failed to register';
        logAuth('register_error', {
          message: err.message,
          status: axiosError.response?.status,
          detail: errorDetail,
        });
        setError(message);
        Alert.alert('Registration Failed', message);
        throw new Error(message);
      }
      throw err;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const initializeAuth = async (): Promise<void> => {
      logAuth('init_auth_check');
      await checkAuthStatus();
    };
    void initializeAuth();
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        error,
        isAuthenticated: !!user,
        isInitialized,
        login,
        logout,
        register,
        checkAuthStatus,
        clearError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
