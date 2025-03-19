# Services Directory

This directory contains service modules for the ADHD Calendar frontend application.

## Overview

The services directory houses modules that handle external communication, data processing, and other non-UI logic. These services act as a layer between the application's UI components and external data sources or APIs.

## Service Categories

### API Services

- **ApiService**: Base service for API communication
- **AuthService**: Authentication API endpoints
- **UserService**: User-related API endpoints
- **TaskService**: Task-related API endpoints
- **CalendarService**: Calendar-related API endpoints

### ML-Related Services

- **ProductivityService**: Productivity pattern analysis and predictions
- **TimeEstimationService**: Task time estimation functionality
- **CommitmentService**: Commitment detection and management
- **CircadianService**: Energy pattern analysis and scheduling

### Storage Services

- **StorageService**: Local storage management
- **CacheService**: Data caching functionality
- **OfflineService**: Offline data handling and synchronization

### Utility Services

- **LoggingService**: Application logging functionality
- **AnalyticsService**: User analytics tracking
- **NotificationService**: Push notification management
- **ErrorReportingService**: Error tracking and reporting

## Service Structure

Services typically follow these patterns:

- Class-based services with methods
- Function-based services with related functions
- Singleton pattern for global services
- Factory pattern for parameterized services

## API Service Example

```typescript
// api.service.ts
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { API_BASE_URL } from '../constants';
import { StorageService } from './storage.service';

class ApiService {
  private client: AxiosInstance;
  private storageService: StorageService;

  constructor() {
    this.storageService = new StorageService();
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    this.client.interceptors.request.use(
      async (config: AxiosRequestConfig) => {
        const token = await this.storageService.getItem('auth_token');
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    this.client.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error) => {
        if (error.response && error.response.status === 401) {
          // Handle authentication error
          this.storageService.removeItem('auth_token');
          // Redirect to login
        }
        return Promise.reject(error);
      }
    );
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get<T>(url, config);
    return response.data;
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post<T>(url, data, config);
    return response.data;
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.put<T>(url, data, config);
    return response.data;
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete<T>(url, config);
    return response.data;
  }
}

export default new ApiService();
```

## Usage with Hooks

Services are typically used within custom hooks:

```typescript
// useTasks.ts
import { useState, useEffect } from 'react';
import { Task } from '../types';
import TaskService from '../services/task.service';

export const useTasks = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await TaskService.getTasks();
      setTasks(data);
    } catch (err) {
      setError(err.message || 'Failed to fetch tasks');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  return {
    tasks,
    loading,
    error,
    fetchTasks,
  };
};
```

## Testing Services

Services are tested with unit tests:

```typescript
// task.service.test.ts
import TaskService from '../services/task.service';
import ApiService from '../services/api.service';

jest.mock('../services/api.service');

describe('TaskService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should fetch tasks', async () => {
    const mockTasks = [{ id: '1', title: 'Test Task' }];
    
    (ApiService.get as jest.Mock).mockResolvedValue(mockTasks);
    
    const tasks = await TaskService.getTasks();
    
    expect(ApiService.get).toHaveBeenCalledWith('/tasks');
    expect(tasks).toEqual(mockTasks);
  });
});
```

## Development Guidelines

When creating services:

1. Follow separation of concerns principles
2. Use TypeScript for type safety
3. Handle errors appropriately
4. Implement proper error handling
5. Use dependency injection for testability
6. Document public methods and interfaces
7. Write unit tests for all services

## Related Documentation

- [API Integration](../docs/api_integration.md)
- [Error Handling](../docs/error_handling.md)
- [Authentication Flow](../docs/authentication_flow.md) 