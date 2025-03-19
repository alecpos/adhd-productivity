import * as LocalAuthentication from 'expo-local-authentication';
import * as SecureStore from 'expo-secure-store';

import { API_ENDPOINTS } from '../../../core/config';
import { api } from '../../../lib/api';

export class SecurityService {
  static async authenticateWithBiometrics(): Promise<boolean> {
    try {
      const hasHardware = await LocalAuthentication.hasHardwareAsync();
      if (!hasHardware) {
        console.warn('[SecurityService] No biometric hardware available');
        return false;
      }

      const isEnrolled = await LocalAuthentication.isEnrolledAsync();
      if (!isEnrolled) {
        console.warn('[SecurityService] No biometrics enrolled');
        return false;
      }

      const result = await LocalAuthentication.authenticateAsync({
        promptMessage: 'Authenticate to access health data',
        disableDeviceFallback: false,
        cancelLabel: 'Cancel',
      });

      return result.success;
    } catch (error) {
      console.error('[SecurityService] Biometric authentication error:', error);
      return false;
    }
  }

  static async storeUserData(key: string, value: string): Promise<void> {
    try {
      await SecureStore.setItemAsync(key, value);
      console.log(`[SecurityService] Data stored successfully for key: ${key}`);
    } catch (error) {
      console.error('[SecurityService] Error storing data:', error);
      throw new Error('Failed to store data securely');
    }
  }

  static async getUserData(key: string): Promise<string | null> {
    try {
      const result = await SecureStore.getItemAsync(key);
      console.log(`[SecurityService] Data retrieved for key: ${key}`);
      return result;
    } catch (error) {
      console.error('[SecurityService] Error retrieving data:', error);
      throw new Error('Failed to retrieve data');
    }
  }

  static async deleteUserData(key: string): Promise<void> {
    try {
      await SecureStore.deleteItemAsync(key);
      console.log(`[SecurityService] Data deleted for key: ${key}`);
    } catch (error) {
      console.error('[SecurityService] Error deleting data:', error);
      throw new Error('Failed to delete data');
    }
  }

  static async exportUserData(key: string): Promise<void> {
    try {
      const data = await this.getUserData(key);
      if (!data) {
        throw new Error('No data to export');
      }

      // Send to backend for secure export
      await api.post(API_ENDPOINTS.HEALTH.EXPORT, {
        data: data,
        key: key,
      });
      
      console.log(`[SecurityService] Data exported successfully for key: ${key}`);
    } catch (error) {
      console.error('[SecurityService] Error exporting data:', error);
      throw new Error('Failed to export data');
    }
  }
} 