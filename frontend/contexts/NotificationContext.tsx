import React, { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { Platform } from 'react-native';

// Define the shape of a notification
interface Notification {
  id: string;
  title: string;
  body: string;
  data?: Record<string, unknown>;
  date?: Date;
}

// Define the context shape
interface NotificationContextType {
  notifications: Notification[];
  addNotification: (notification: Omit<Notification, 'id'>) => void;
  removeNotification: (id: string) => void;
  clearAllNotifications: () => void;
  isPermissionGranted: boolean;
  requestPermissions: () => Promise<boolean>;
}

// Create the context with a default value
const NotificationContext = createContext<NotificationContextType>({
  notifications: [],
  addNotification: () => {},
  removeNotification: () => {},
  clearAllNotifications: () => {},
  isPermissionGranted: false,
  requestPermissions: async () => false,
});

// Hook for using the notification context
export const useNotifications = (): NotificationContextType => useContext(NotificationContext);

interface NotificationProviderProps {
  children: ReactNode;
}

export const NotificationProvider: React.FC<NotificationProviderProps> = ({ children }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isPermissionGranted, setIsPermissionGranted] = useState(false);
  
  // Request permissions when the provider is mounted
  useEffect(() => {
    // For web or environments without notification permissions, we just mark it as true
    if (Platform.OS === 'web') {
      setIsPermissionGranted(true);
    }
  }, []);
  
  // Function to request permissions - simplified implementation
  const requestPermissions = async (): Promise<boolean> => {
    try {
      // On web, just return true
      if (Platform.OS === 'web') {
        setIsPermissionGranted(true);
        return true;
      }
      
      // Simulate permission being granted
      setIsPermissionGranted(true);
      return true;
    } catch (error) {
      console.error('Error requesting notification permissions:', error);
      return false;
    }
  };
  
  // Add a notification
  const addNotification = (notification: Omit<Notification, 'id'>): void => {
    const newNotification: Notification = {
      ...notification,
      id: Math.random().toString(36).substring(2, 15),
    };
    
    setNotifications((prevNotifications) => [...prevNotifications, newNotification]);
  };
  
  // Remove a notification
  const removeNotification = (id: string): void => {
    setNotifications((prevNotifications) => 
      prevNotifications.filter((notification) => notification.id !== id)
    );
  };
  
  // Clear all notifications
  const clearAllNotifications = (): void => {
    setNotifications([]);
  };
  
  return (
    <NotificationContext.Provider
      value={{
        notifications,
        addNotification,
        removeNotification,
        clearAllNotifications,
        isPermissionGranted,
        requestPermissions,
      }}
    >
      {children}
    </NotificationContext.Provider>
  );
};

export default NotificationContext; 