import * as Haptics from 'expo-haptics';
import { Platform } from 'react-native';

// Check if we're on web
const isWeb = Platform.OS === 'web';

// Create safe functions that won't break on web
export const triggerImpactLight = async (): Promise<void> => {
  if (!isWeb) {
    try {
      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    } catch (error) {
      console.warn('Haptics not available:', error);
    }
  }
};

export const triggerImpactMedium = async (): Promise<void> => {
  if (!isWeb) {
    try {
      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    } catch (error) {
      console.warn('Haptics not available:', error);
    }
  }
};

export const triggerImpactHeavy = async (): Promise<void> => {
  if (!isWeb) {
    try {
      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
    } catch (error) {
      console.warn('Haptics not available:', error);
    }
  }
};

export const triggerNotification = async (type = Haptics.NotificationFeedbackType.Success): Promise<void> => {
  if (!isWeb) {
    try {
      await Haptics.notificationAsync(type);
    } catch (error) {
      console.warn('Haptics not available:', error);
    }
  }
};

export const triggerSelection = async (): Promise<void> => {
  if (!isWeb) {
    try {
      await Haptics.selectionAsync();
    } catch (error) {
      console.warn('Haptics not available:', error);
    }
  }
};

// Default export for convenience
export default {
  triggerImpactLight,
  triggerImpactMedium,
  triggerImpactHeavy,
  triggerNotification,
  triggerSelection
}; 