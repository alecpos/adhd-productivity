# Frontend Architecture

This document provides an overview of the ADHD Calendar frontend architecture, including its technical stack, organization, and key design patterns.

## Technology Stack

The ADHD Calendar frontend is built using the following technologies:

- **React Native (Expo)**: Cross-platform mobile application framework
- **TypeScript**: For type-safe JavaScript development
- **Expo Router**: For navigation and routing
- **@rneui/themed**: For theming and UI components
- **React Navigation**: For navigation structure
- **Zustand**: For state management
- **Axios**: For API requests
- **date-fns**: For date manipulation
- **i18next**: For internationalization
- **React Hook Form**: For form handling and validation
- **Victory Native**: For data visualization (charts/graphs)
- **Lottie**: For animations

## Project Structure

The frontend codebase is organized in a feature-based directory structure:

```
frontend/
├── app/                 # Expo Router app directory
├── assets/              # Static assets (images, fonts, etc.)
├── components/          # Reusable UI components
├── contexts/            # React contexts (ThemeContext, AuthContext, etc.)
├── core/                # Core utilities and configurations
│   ├── api/             # API service integration
│   └── config/          # App configuration
├── hooks/               # Custom React hooks
├── navigation/          # Navigation configuration
├── screens/             # Screen components
├── services/            # Business logic services
├── theme/               # Theming system
├── types/               # TypeScript type definitions
└── utils/               # Utility functions
```

## Key Architectural Patterns

### State Management

The application uses a combination of state management approaches:

1. **Zustand**: For global application state
2. **React Context**: For theme, authentication, and feature-specific state
3. **Local Component State**: For UI-specific state

Example Zustand store:

```typescript
import create from 'zustand';

interface TaskStore {
  tasks: Task[];
  isLoading: boolean;
  fetchTasks: () => Promise<void>;
  addTask: (task: Task) => Promise<void>;
  // ... other actions
}

export const useTaskStore = create<TaskStore>((set) => ({
  tasks: [],
  isLoading: false,
  fetchTasks: async () => {
    set({ isLoading: true });
    try {
      const response = await api.getTasks();
      set({ tasks: response.data, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      // Handle error
    }
  },
  addTask: async (task) => {
    try {
      await api.createTask(task);
      set((state) => ({ tasks: [...state.tasks, task] }));
    } catch (error) {
      // Handle error
    }
  },
  // ... other actions
}));
```

### API Integration

API interactions are handled through a service-based architecture:

1. **API Client**: Axios-based client with interceptors for authentication and error handling
2. **Service Modules**: Feature-specific API service modules
3. **React Query**: For data fetching, caching, and synchronization

### Navigation

The app uses Expo Router for file-based navigation, providing a simple and maintainable routing system:

```
app/
├── index.tsx            # Home screen
├── tasks/
│   ├── index.tsx        # Tasks list screen
│   └── [id].tsx         # Task detail screen (dynamic route)
├── calendar/
│   ├── index.tsx        # Calendar screen
│   └── [date].tsx       # Specific date view (dynamic route)
└── settings/
    └── index.tsx        # Settings screen
```

### ADHD-Specific Architecture Considerations

The architecture is specifically designed to support users with ADHD:

1. **Reduced Cognitive Load**: Simple, consistent UI patterns and minimal visual clutter
2. **Error Recovery**: Robust error handling and automatic recovery
3. **Offline Support**: Critical features work offline with background synchronization
4. **Adaptability**: User interface adapts to individual ADHD presentation and preferences
5. **Reduced Executive Function Demands**: Smart defaults and simplified workflows

## Authentication Flow

The authentication process uses JWT tokens with secure storage:

1. User credentials are sent to the authentication API
2. JWT tokens (access and refresh) are received and stored securely
3. Access token is included in subsequent API requests
4. Refresh token is used to obtain a new access token when needed
5. Biometric authentication is supported for improved UX

## Theming System

The app uses a comprehensive theming system to support accessibility preferences:

```typescript
const theme = {
  colors: {
    primary: '#4A6FA5',
    secondary: '#53B4DF',
    background: '#FFFFFF',
    // ... other colors including high-contrast alternatives
  },
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
  },
  fontSize: {
    sm: 12,
    md: 16,
    lg: 20,
    xl: 24,
  },
  borderRadius: {
    sm: 4,
    md: 8,
    lg: 12,
  },
  // ... other theme properties
};
```

## Testing Strategy

The frontend implements a comprehensive testing strategy:

1. **Unit Tests**: For utility functions and hooks (Jest)
2. **Component Tests**: For UI components (Testing Library)
3. **Integration Tests**: For feature workflows
4. **E2E Tests**: For critical user journeys

## Performance Optimization

Key performance optimization strategies include:

1. **Lazy Loading**: Components and screens are loaded on demand
2. **Memoization**: React.memo and useMemo for expensive computations
3. **Asset Optimization**: Images and animations are optimized for mobile
4. **Virtualized Lists**: FlatList and SectionList for large data sets
5. **Background Processing**: Heavy computations run in background threads

## Accessibility

Accessibility is a core concern, with special attention to:

1. **Screen Reader Support**: All components support screen readers
2. **Keyboard Navigation**: For web version
3. **Adjustable Text Size**: Dynamic text scaling
4. **Color Contrast**: High contrast modes for different visual needs
5. **Reduced Motion**: Options to reduce animations
6. **ADHD-Specific Accommodations**: Visual simplification, focus aids, etc.

## Build and Deployment

The app uses Expo's build system for deployment:

1. **Development**: Expo Go app for rapid iteration
2. **Testing**: EAS Build for test builds
3. **Production**: EAS Build for production builds
4. **Updates**: EAS Update for over-the-air updates
5. **Distribution**: App Store (iOS) and Google Play (Android) 