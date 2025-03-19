import axios from 'axios';

import { AppError } from '../types/error';

import api from './api';

import type { User } from '../types/user';





interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

interface LoginCredentials {
  username: string;
  password: string;
}

interface RegisterCredentials extends LoginCredentials {
  email: string;
}

export const signIn = async (username: string, password: string): Promise<AuthResponse> => {
  try {
    const response = await api.post<AuthResponse>('/auth/login', {
      username,
      password
    });
    return response.data;
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      throw new AppError(
        error.response?.data?.detail || 'Login failed',
        'AUTH_ERROR',
        error.response?.status
      );
    }
    throw new AppError('An unexpected error occurred during login', 'UNKNOWN_ERROR');
  }
};

export const signUp = async (username: string, password: string, email: string): Promise<void> => {
  try {
    await api.post('/auth/register', {
      username,
      password,
      email
    });
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      throw new AppError(
        error.response?.data?.detail || 'Registration failed',
        'AUTH_ERROR',
        error.response?.status
      );
    }
    throw new AppError('An unexpected error occurred during registration', 'UNKNOWN_ERROR');
  }
};

export const signOut = async (): Promise<void> => {
  try {
    await api.post('/auth/logout');
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new AppError(
        error.response?.data?.detail || 'Logout failed',
        'AUTH_ERROR',
        error.response?.status
      );
    }
    throw new AppError('An unexpected error occurred during logout', 'UNKNOWN_ERROR');
  }
};

export const verifyToken = async (): Promise<User> => {
  try {
    const response = await api.get<{ user: User }>('/auth/verify');
    return response.data.user;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new AppError(
        error.response?.data?.detail || 'Token verification failed',
        'AUTH_ERROR',
        error.response?.status
      );
    }
    throw new AppError('An unexpected error occurred during token verification', 'UNKNOWN_ERROR');
  }
};

export const refreshToken = async (refresh_token: string): Promise<AuthResponse> => {
  try {
    const response = await api.post<AuthResponse>('/auth/refresh', { refresh_token });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new AppError(
        error.response?.data?.detail || 'Token refresh failed',
        'AUTH_ERROR',
        error.response?.status
      );
    }
    throw new AppError('An unexpected error occurred during token refresh', 'UNKNOWN_ERROR');
  }
}; 