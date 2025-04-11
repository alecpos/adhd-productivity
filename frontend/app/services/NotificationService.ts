import Constants from 'expo-constants';
import { Platform } from 'react-native';

import { isNotificationSubscription } from '../types/notifications';

import type {
  NotificationRequest,
  NotificationResponse,
  NotificationTriggerInput,
  Notification,
  NotificationsModuleType
} from '../types/notifications';

interface ExpoConfig {
  extra?: {
    eas?: {
      projectId?: string;
    };
  };
}

// Only import notifications if not on web
let NotificationsModule: NotificationsModuleType | null = null;

if (Platform.OS !== 'web') {
  NotificationsModule = require('expo-notifications') as NotificationsModuleType;
}

class NotificationService {
  private static instance: NotificationService | null = null;
  private isWeb: boolean;

  private constructor() {
    this.isWeb = Platform.OS === 'web';
  }

  public static getInstance(): NotificationService {
    if (NotificationService.instance === null) {
      NotificationService.instance = new NotificationService();
    }
    return NotificationService.instance;
  }

  private getProjectId(): string | undefined {
    const config = Constants.expoConfig as ExpoConfig | undefined;
    return config?.extra?.eas?.projectId;
  }

  public async initialize(): Promise<void> {
    if (this.isWeb) {
      console.warn('Notifications are not supported in web environment');
      return;
    }

    try {
      const projectId = this.getProjectId();
      if (!NotificationsModule || !projectId) {
        console.warn('Notifications are only supported in EAS builds');
        return;
      }

      const { status: existingStatus } = await NotificationsModule.getPermissionsAsync();
      let finalStatus = existingStatus;

      if (existingStatus !== 'granted') {
        const { status } = await NotificationsModule.requestPermissionsAsync();
        finalStatus = status;
      }

      if (finalStatus !== 'granted') {
        console.warn('Failed to get push token for push notification!');
        return;
      }

      if (Platform.OS === 'android') {
        await NotificationsModule.setNotificationChannelAsync('default', {
          name: 'default',
          importance: NotificationsModule.AndroidImportance.MAX,
          vibrationPattern: [0, 250, 250, 250],
          lightColor: '#FF231F7C',
        });
      }

      NotificationsModule.setNotificationHandler({
        handleNotification: async () => ({
          shouldShowAlert: true,
          shouldPlaySound: true,
          shouldSetBadge: true,
        }),
      });
    } catch (error) {
      console.warn('Error initializing notifications:', error);
    }
  }

  public async getToken(): Promise<string | null> {
    if (this.isWeb) {
      console.warn('Push tokens are not supported in web environment');
      return null;
    }

    try {
      const projectId = this.getProjectId();
      if (!NotificationsModule || !projectId) {
        return null;
      }

      const token = await NotificationsModule.getExpoPushTokenAsync({ projectId });
      return token.data;
    } catch (error) {
      console.warn('Error getting push token:', error);
      return null;
    }
  }

  public async scheduleLocalNotification(
    title: string,
    body: string,
    trigger?: NotificationTriggerInput
  ): Promise<string | null> {
    if (this.isWeb || !NotificationsModule) {
      console.warn('Local notifications are not supported in web environment');
      return null;
    }

    try {
      const request: NotificationRequest = {
        identifier: Date.now().toString(),
        content: {
          title,
          body,
          data: {},
          sound: 'default',
          subtitle: null
        },
        trigger: trigger ?? null,
      };

      return await NotificationsModule.scheduleNotificationAsync(request);
    } catch (error) {
      console.warn('Error scheduling notification:', error);
      return null;
    }
  }

  public addNotificationReceivedListener(
    listener: (event: Notification) => void
  ): (() => void) | null {
    if (this.isWeb || !NotificationsModule) {
      console.warn('Notification listeners are not supported in web environment');
      return null;
    }

    try {
      const subscription = NotificationsModule.addNotificationReceivedListener(listener);
      const cleanup = (): void => {
        if (isNotificationSubscription(subscription)) {
          subscription.remove();
        }
      };
      return cleanup;
    } catch (error) {
      if (error instanceof Error) {
        console.warn('Error adding notification received listener:', error.message);
      } else {
        console.warn('Error adding notification received listener:', error);
      }
      return null;
    }
  }

  public addNotificationResponseReceivedListener(
    listener: (response: NotificationResponse) => void
  ): (() => void) | null {
    if (this.isWeb || !NotificationsModule) {
      console.warn('Notification listeners are not supported in web environment');
      return null;
    }

    try {
      const subscription = NotificationsModule.addNotificationResponseReceivedListener(listener);
      const cleanup = (): void => {
        if (isNotificationSubscription(subscription)) {
          subscription.remove();
        }
      };
      return cleanup;
    } catch (error) {
      if (error instanceof Error) {
        console.warn('Error adding notification response listener:', error.message);
      } else {
        console.warn('Error adding notification response listener:', error);
      }
      return null;
    }
  }
}

export default NotificationService;
