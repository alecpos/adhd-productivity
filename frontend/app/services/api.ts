import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';

// Create base axios instance
const api = axios.create({
  baseURL: process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for auth token
api.interceptors.request.use(
  async (config) => {
    try {
      const token = await AsyncStorage.getItem('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (error) {
      console.error('Error getting auth token:', error);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Handle 401 Unauthorized errors
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Try to refresh token
        const refreshToken = await AsyncStorage.getItem('refreshToken');
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        const response = await api.post('/auth/refresh', {
          refresh_token: refreshToken,
        });

        const { access_token } = response.data;
        await AsyncStorage.setItem('token', access_token);

        // Retry the original request
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Clear tokens and redirect to login
        await AsyncStorage.multiRemove(['token', 'refreshToken']);
        // You might want to add navigation logic here
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Add logging interceptor for development
if (__DEV__) {
  api.interceptors.request.use((config) => {
    console.log('API Request:', {
      method: config.method,
      url: config.url,
      data: config.data,
      headers: config.headers,
    });
    return config;
  });

  api.interceptors.response.use(
    (response) => {
      console.log('API Response:', {
        status: response.status,
        data: response.data,
        headers: response.headers,
      });
      return response;
    },
    (error) => {
      console.error('API Error:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
      });
      return Promise.reject(error);
    }
  );
}

export default api;
