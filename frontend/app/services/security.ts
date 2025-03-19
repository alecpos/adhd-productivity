import CryptoJS from 'crypto-js';
import Constants from 'expo-constants';
import * as Crypto from 'expo-crypto';
import * as FileSystem from 'expo-file-system';
import * as LocalAuthentication from 'expo-local-authentication';
import * as SecureStore from 'expo-secure-store';
import * as Sharing from 'expo-sharing';

import { api } from '@/lib/api';

interface AuditEventDetails {
  ip?: string;
  userAgent?: string;
  location?: string;
  deviceId?: string;
  resourceType?: string;
  changes?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
}

interface AuditEvent {
  action: string;
  userId: string;
  resourceId: string;
  timestamp?: string;
  details?: AuditEventDetails;
}

// Constants for encryption
let ENCRYPTION_KEY = Constants.expoConfig?.extra?.EXPO_PUBLIC_ENCRYPTION_KEY || process.env.EXPO_PUBLIC_ENCRYPTION_KEY;
if (!ENCRYPTION_KEY) {
  console.warn('Encryption key not found in environment variables, using fallback key');
  ENCRYPTION_KEY = 'development_fallback_key';
}
const PHI_STORAGE_KEY = 'protected_health_info';

interface MedicalData {
  diagnoses: string[];
  medications: Array<{
    name: string;
    dosage: string;
    frequency: string;
    startDate?: string;
    endDate?: string;
  }>;
  allergies: string[];
  conditions: string[];
  notes: string;
  lastUpdated: string;
}

export interface ProtectedHealthInfo {
  id: string;
  patientId: string;
  data: MedicalData;
  createdAt: string;
  updatedAt: string;
}

interface ActivityPattern {
  timeOfDay: string;
  productivity: number;
  energyLevel: number;
  focusScore: number;
  frequency: number;
}

export interface ExportData {
  user_info: {
    id: string;
    email: string;
    name: string;
    created_at: string;
  };
  analytics: {
    total_tasks_completed: number;
    average_task_completion_time: number;
    focus_time: number;
    productivity_score: number | null;
    activity_patterns: ActivityPattern[];
  };
  tasks: Array<{
    id: string;
    title: string;
    description: string;
    status: string;
    priority: string;
    created_at: string;
    completed_at: string | null;
    estimated_duration: number;
    actual_duration: number;
  }>;
  mental_health_logs: Array<{
    id: string;
    mood: string;
    energy_level: number;
    notes: string;
    timestamp: string;
  }>;
  energy_logs: Array<{
    id: string;
    energy_level: number;
    activity: string;
    notes: string;
    timestamp: string;
  }>;
  focus_sessions: {
    hyperfocus: Array<{
      id: string;
      start_time: string;
      end_time: string | null;
      duration: number;
    }>;
    pomodoro: Array<{
      id: string;
      start_time: string;
      completed_pomodoros: number;
      work_duration: number;
    }>;
  };
  export_info: {
    generated_at: string;
    date_range: {
      start: string;
      end: string;
    };
  };
}

export class SecurityService {
  async logAuditEvent(event: AuditEvent): Promise<void> {
    try {
      await api.post('/audit/log', {
        ...event,
        timestamp: event.timestamp || new Date().toISOString(),
      });
    } catch (error) {
      console.error('Error logging audit event:', error);
      // Don't throw error to prevent blocking operations
    }
  }

  // Biometric authentication
  async authenticateWithBiometrics(): Promise<boolean> {
    try {
      const hasHardware = await LocalAuthentication.hasHardwareAsync();
      if (!hasHardware) {
        console.warn('Device does not support biometric authentication');
        return false;
      }

      const isEnrolled = await LocalAuthentication.isEnrolledAsync();
      if (!isEnrolled) {
        console.warn('No biometrics enrolled on this device');
        return false;
      }

      const result = await LocalAuthentication.authenticateAsync({
        promptMessage: 'Authenticate to access medical information',
        disableDeviceFallback: false,
      });

      return result.success;
    } catch (error) {
      console.error('Biometric authentication error:', error);
      return false;
    }
  }

  // Encrypt data
  private encryptData<T>(data: T): string {
    try {
      const jsonString = JSON.stringify(data);
      return CryptoJS.AES.encrypt(jsonString, ENCRYPTION_KEY).toString();
    } catch (error) {
      console.error('Encryption error:', error);
      throw new Error('Failed to encrypt data');
    }
  }

  // Decrypt data
  private decryptData<T>(encryptedData: string): T {
    try {
      const bytes = CryptoJS.AES.decrypt(encryptedData, ENCRYPTION_KEY);
      const decryptedString = bytes.toString(CryptoJS.enc.Utf8);
      return JSON.parse(decryptedString);
    } catch (error) {
      console.error('Decryption error:', error);
      throw new Error('Failed to decrypt data');
    }
  }

  // Store Protected Health Information (PHI)
  async storePHI(phi: ProtectedHealthInfo): Promise<void> {
    try {
      const encryptedData = this.encryptData(phi);
      await SecureStore.setItemAsync(PHI_STORAGE_KEY, encryptedData);
    } catch (error) {
      console.error('Error storing PHI:', error);
      throw new Error('Failed to store protected health information');
    }
  }

  // Retrieve Protected Health Information (PHI)
  async retrievePHI(): Promise<ProtectedHealthInfo | null> {
    try {
      const encryptedData = await SecureStore.getItemAsync(PHI_STORAGE_KEY);
      if (!encryptedData) return null;
      return this.decryptData<ProtectedHealthInfo>(encryptedData);
    } catch (error) {
      console.error('Error retrieving PHI:', error);
      throw new Error('Failed to retrieve protected health information');
    }
  }

  // Export user data
  async exportUserData(userId: string, startDate?: Date, endDate?: Date): Promise<void> {
    try {
      // First, authenticate the user
      const isAuthenticated = await this.authenticateWithBiometrics();
      if (!isAuthenticated) {
        throw new Error('Authentication required for data export');
      }

      // Get data from backend
      const response = await api.get<ExportData>(`/analytics/user/${userId}/export`, {
        params: {
          start_date: startDate?.toISOString(),
          end_date: endDate?.toISOString(),
        },
      });

      // Generate summary
      const summary = await this.generateDataExportSummary(response.data);
      console.log(summary);

      // Create a temporary file with the exported data
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const fileName = `adhd_assistant_data_export_${timestamp}.json`;
      const fileUri = `${FileSystem.documentDirectory}${fileName}`;

      // Encrypt the data before writing to file
      const encryptedData = this.encryptData(response.data);

      // Write the encrypted data to a file
      await FileSystem.writeAsStringAsync(
        fileUri,
        encryptedData,
        {
          encoding: FileSystem.EncodingType.UTF8,
        }
      );

      // Check if sharing is available
      const isSharingAvailable = await Sharing.isAvailableAsync();
      if (!isSharingAvailable) {
        throw new Error('Sharing is not available on this device');
      }

      // Share the file
      await Sharing.shareAsync(fileUri, {
        mimeType: 'application/json',
        dialogTitle: 'Export Health Data',
        UTI: 'public.json',
      });

      // Clean up the temporary file
      await FileSystem.deleteAsync(fileUri);
    } catch (error) {
      console.error('Error exporting data:', error);
      throw new Error('Failed to export data');
    }
  }

  // Generate a summary of the exported data
  async generateDataExportSummary(data: ExportData): Promise<string> {
    const summary = {
      totalTasks: data.tasks?.length || 0,
      completedTasks: data.tasks?.filter(t => t.completed_at)?.length || 0,
      totalMentalHealthLogs: data.mental_health_logs?.length || 0,
      totalEnergyLogs: data.energy_logs?.length || 0,
      totalFocusSessions: (
        (data.focus_sessions?.hyperfocus?.length || 0) +
        (data.focus_sessions?.pomodoro?.length || 0)
      ),
    };

    return `Data Export Summary:
      - Total Tasks: ${summary.totalTasks}
      - Completed Tasks: ${summary.completedTasks}
      - Mental Health Logs: ${summary.totalMentalHealthLogs}
      - Energy Logs: ${summary.totalEnergyLogs}
      - Focus Sessions: ${summary.totalFocusSessions}
    `;
  }

  // Delete user data
  async deleteUserData(userId: string): Promise<void> {
    try {
      await SecureStore.deleteItemAsync(PHI_STORAGE_KEY);
      // Additional cleanup if needed
    } catch (error) {
      console.error('Data deletion error:', error);
      throw new Error('Failed to delete user data');
    }
  }
}

export const securityService = new SecurityService(); 