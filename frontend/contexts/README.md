# Contexts Directory

This directory contains React Context providers and hooks for the ADHD Calendar frontend application.

## Overview

The contexts directory houses React Context providers that manage global or shared state across components. These contexts establish a way to share values between components without explicitly passing props through every level of the component tree.

## Context Categories

### Authentication Context

- **AuthContext**: Manages authentication state and methods
- Provides user authentication status, user profile, and auth-related functions
- Used for protecting routes and conditionally rendering UI elements

### Theme Context

- **ThemeContext**: Manages application theme
- Provides theme values, modes (light/dark), and customization options
- Used for consistent styling across the application

### Settings Context

- **SettingsContext**: Manages user settings and preferences
- Provides app-wide configuration and user preferences
- Used for customizing the user experience

### ML-Related Contexts

- **ProductivityContext**: Provides productivity pattern data and insights
- **CircadianContext**: Manages circadian rhythm and energy level information
- **TimeEstimationContext**: Provides time estimation functionality

## Context Structure

Each context typically includes:

- Context definition with TypeScript interface
- Provider component that manages state
- Custom hook for consuming the context
- Initial/default values

## Context Example

```tsx
// auth-context.tsx
import React, { createContext, useState, useContext, useEffect } from 'react';
import { User } from '../types';
import { AuthService } from '../services';

interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider: React.FC<React.PropsWithChildren<{}>> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for existing auth on mount
    const checkAuth = async () => {
      try {
        const userData = await AuthService.getCurrentUser();
        setUser(userData);
      } catch (error) {
        // Handle error (user not authenticated)
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const userData = await AuthService.login(email, password);
      setUser(userData);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    try {
      await AuthService.logout();
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (userData: RegisterData) => {
    setIsLoading(true);
    try {
      await AuthService.register(userData);
      // Optionally auto-login after registration
      // await login(userData.email, userData.password);
    } finally {
      setIsLoading(false);
    }
  };

  const value = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
    register,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextValue => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
```

## Usage Example

```tsx
// App.tsx - Provider setup
import React from 'react';
import { AuthProvider } from './contexts/auth-context';
import { ThemeProvider } from './contexts/theme-context';
import { SettingsProvider } from './contexts/settings-context';
import Navigation from './navigation';

const App = () => {
  return (
    <AuthProvider>
      <ThemeProvider>
        <SettingsProvider>
          <Navigation />
        </SettingsProvider>
      </ThemeProvider>
    </AuthProvider>
  );
};

// Component using context
import React from 'react';
import { View, Text, Button } from 'react-native';
import { useAuth } from '../contexts/auth-context';

const LoginScreen = () => {
  const { login, isLoading } = useAuth();

  const handleLogin = async () => {
    try {
      await login('user@example.com', 'password123');
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <View>
      <Text>Login Screen</Text>
      <Button
        title={isLoading ? 'Logging in...' : 'Login'}
        onPress={handleLogin}
        disabled={isLoading}
      />
    </View>
  );
};
```

## Testing Contexts

Contexts are tested with dedicated test utilities:

```tsx
// auth-context.test.tsx
import React from 'react';
import { render, act, waitFor } from '@testing-library/react-native';
import { AuthProvider, useAuth } from '../contexts/auth-context';
import { AuthService } from '../services';

jest.mock('../services');

const TestComponent = () => {
  const { user, isAuthenticated } = useAuth();
  return (
    <View>
      <Text testID="auth-status">
        {isAuthenticated ? 'Authenticated' : 'Not authenticated'}
      </Text>
      {user && <Text testID="user-email">{user.email}</Text>}
    </View>
  );
};

describe('AuthContext', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should provide authentication status', async () => {
    const mockUser = { id: '1', email: 'user@example.com' };
    AuthService.getCurrentUser.mockResolvedValue(mockUser);

    const { getByTestId } = render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(getByTestId('auth-status')).toHaveTextContent('Authenticated');
      expect(getByTestId('user-email')).toHaveTextContent('user@example.com');
    });
  });
});
```

## Development Guidelines

When creating new contexts:

1. Only use contexts for truly shared state
2. Keep context values focused on specific concerns
3. Provide clear TypeScript interfaces
4. Implement custom hooks for consuming contexts
5. Handle loading and error states
6. Document the context's purpose and usage
7. Write tests for context providers and consumers

## Related Documentation

- [React Context API](https://reactjs.org/docs/context.html)
- [State Management Guide](../docs/state_management.md)
- [Context Design Patterns](../docs/context_patterns.md) 