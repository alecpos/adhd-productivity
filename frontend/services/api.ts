import axios from 'axios';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to handle auth
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add request interceptor to handle offline scenarios
api.interceptors.request.use(async (config) => {
  if (!navigator.onLine) {
    // Return cached data if available
    const cachedData = localStorage.getItem(`cache_${config.url}`);
    if (cachedData) {
      return Promise.reject({
        isOffline: true,
        cachedData: JSON.parse(cachedData)
      });
    }
    return Promise.reject({
      isOffline: true,
      message: 'You are offline. Some features may be limited.'
    });
  }
  return config;
});

// Add response interceptor to handle errors
api.interceptors.response.use(
  (response) => {
    // Cache successful GET requests
    if (response.config.method?.toLowerCase() === 'get') {
      localStorage.setItem(
        `cache_${response.config.url}`,
        JSON.stringify(response.data)
      );
    }
    return response;
  },
  (error) => {
    if (error.isOffline) {
      return Promise.reject(error);
    }
    
    if (!error.response) {
      return Promise.reject({
        message: 'Network error. Please check your connection.'
      });
    }
    
    if (error.response) {
      // Handle specific error codes
      switch (error.response.status) {
        case 401:
          // Handle unauthorized
          localStorage.removeItem('token');
          window.location.href = '/login';
          break;
        case 404:
          // Handle not found
          console.error('Resource not found:', error.response.config.url);
          break;
        case 500:
          // Handle server error
          console.error('Server error:', error.response.data);
          break;
        default:
          console.error('API error:', error.response.data);
      }
    }
    return Promise.reject(error);
  }
); 