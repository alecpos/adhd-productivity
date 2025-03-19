// This is a mock version of expo-notifications for web compatibility

// Define the handler interface
interface NotificationHandler {
  handleNotification: () => Promise<{
    shouldShowAlert: boolean;
    shouldPlaySound: boolean;
    shouldSetBadge: boolean;
  }>;
}

let handler: NotificationHandler = {
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
};

// Mock the setNotificationHandler function
export function setNotificationHandler(newHandler: NotificationHandler): void {
  handler = newHandler;
}

// Mock other commonly used functions
export async function scheduleNotificationAsync(options: any): Promise<string> {
  console.warn('expo-notifications is mocked - scheduleNotificationAsync called with:', options);
  return 'mock-notification-id';
}

export async function cancelScheduledNotificationAsync(identifier: string): Promise<void> {
  console.warn('expo-notifications is mocked - cancelScheduledNotificationAsync called with:', identifier);
}

export async function dismissNotificationAsync(identifier: string): Promise<void> {
  console.warn('expo-notifications is mocked - dismissNotificationAsync called with:', identifier);
}

export async function dismissAllNotificationsAsync(): Promise<void> {
  console.warn('expo-notifications is mocked - dismissAllNotificationsAsync called');
}

export async function getLastNotificationResponseAsync(): Promise<null> {
  console.warn('expo-notifications is mocked - getLastNotificationResponseAsync called');
  return null;
}

export async function getPresentedNotificationsAsync(): Promise<any[]> {
  console.warn('expo-notifications is mocked - getPresentedNotificationsAsync called');
  return [];
}

// Default export
export default {
  setNotificationHandler,
  scheduleNotificationAsync,
  cancelScheduledNotificationAsync,
  dismissNotificationAsync,
  dismissAllNotificationsAsync,
  getLastNotificationResponseAsync,
  getPresentedNotificationsAsync,
}; 