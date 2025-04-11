import type {
  NotificationRequest,
  NotificationResponse,
  NotificationTriggerInput,
  Notification,
  AndroidImportance
} from 'expo-notifications';

export interface NotificationSubscription {
  remove: () => void;
}

export interface NotificationsModuleType {
  getPermissionsAsync: () => Promise<{ status: 'granted' | 'undetermined' | 'denied' }>;
  requestPermissionsAsync: () => Promise<{ status: 'granted' | 'undetermined' | 'denied' }>;
  setNotificationChannelAsync: (
    name: string,
    config: {
      name: string;
      importance: AndroidImportance;
      vibrationPattern: number[];
      lightColor: string
    }
  ) => Promise<void>;
  setNotificationHandler: (
    handler: {
      handleNotification: () => Promise<{
        shouldShowAlert: boolean;
        shouldPlaySound: boolean;
        shouldSetBadge: boolean
      }>
    }
  ) => void;
  getExpoPushTokenAsync: (options: { projectId: string }) => Promise<{ data: string }>;
  scheduleNotificationAsync: (request: NotificationRequest) => Promise<string>;
  addNotificationReceivedListener: (listener: (notification: Notification) => void) => NotificationSubscription;
  addNotificationResponseReceivedListener: (listener: (response: NotificationResponse) => void) => NotificationSubscription;
  AndroidImportance: { MAX: AndroidImportance };
}

// Type guard for NotificationSubscription
export function isNotificationSubscription(value: unknown): value is NotificationSubscription {
  return (
    typeof value === 'object' &&
    value !== null &&
    'remove' in value &&
    typeof (value as NotificationSubscription).remove === 'function'
  );
}

export type {
  NotificationRequest,
  NotificationResponse,
  NotificationTriggerInput,
  Notification,
  AndroidImportance
};
