import * as configcat from 'configcat-js';
import Constants from 'expo-constants';

type SettingValue = string | number | boolean | null;

const SDK_KEY = Constants.expoConfig?.extra?.EXPO_PUBLIC_CONFIGCAT_SDK_KEY;

if (!SDK_KEY) {
  console.warn('ConfigCat SDK key is not set. Feature flags will default to false.');
}

// Initialize the client only if we have a valid SDK key
const configCatClient = SDK_KEY ? configcat.getClient(SDK_KEY) : null;

export const featureFlags = {
  async getFlag(key: string): Promise<boolean> {
    try {
      if (!configCatClient) return false;
      return await configCatClient.getValueAsync(key, false);
    } catch (error) {
      console.error('Error fetching feature flag:', error);
      return false;
    }
  },

  async getValue<T extends SettingValue>(key: string, defaultValue: T): Promise<T> {
    try {
      if (!configCatClient) return defaultValue;
      const value = await configCatClient.getValueAsync(key, defaultValue);
      return value;
    } catch (error) {
      console.error('Error fetching feature value:', error);
      return defaultValue;
    }
  }
}; 