import React, { createContext, useContext, useState } from 'react';

import { SecurityService } from '@/core/api/services/securityService';

interface HealthData {
  id: string;
  patientId: string;
  data: any;
  timestamp: string;
  createdAt: string;
  updatedAt: string;
}

interface MedicalContextType {
  isAuthenticated: boolean;
  loading: boolean;
  healthData: HealthData | null;
  error: string | null;
  authenticate: () => Promise<void>;
  storeHealthData: (data: Omit<HealthData, 'timestamp'>) => Promise<void>;
  exportData: () => Promise<void>;
  deleteData: () => Promise<void>;
  clearHealthData: () => void;
}

const MedicalContext = createContext<MedicalContextType | undefined>(undefined);

export function useMedical() {
  const context = useContext(MedicalContext);
  if (!context) {
    throw new Error('useMedical must be used within a MedicalProvider');
  }
  return context;
}

export function MedicalProvider({ children }: { children: React.ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(false);
  const [healthData, setHealthData] = useState<HealthData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const authenticate = async () => {
    console.log('[MedicalContext] Starting authentication');
    try {
      setLoading(true);
      const authenticated = await SecurityService.authenticateWithBiometrics();
      console.log('[MedicalContext] Authentication result:', authenticated);
      setIsAuthenticated(authenticated);
      if (!authenticated) {
        throw new Error('Authentication failed');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Authentication failed';
      console.error('[MedicalContext] Authentication error:', err);
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const storeHealthData = async (data: Omit<HealthData, 'timestamp'>) => {
    console.log('[MedicalContext] Storing health data:', data);
    try {
      setLoading(true);
      setError(null);
      if (!isAuthenticated) {
        throw new Error('Not authenticated');
      }
      const timestamp = new Date().toISOString();
      const newHealthData = { ...data, timestamp };
      console.log('[MedicalContext] Storing data in secure storage');
      await SecurityService.storeUserData('healthData', JSON.stringify(newHealthData));
      setHealthData(newHealthData as HealthData);
      console.log('[MedicalContext] Health data stored successfully');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to store health data';
      console.error('[MedicalContext] Error storing health data:', err);
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const exportData = async () => {
    console.log('[MedicalContext] Starting data export');
    try {
      setLoading(true);
      setError(null);
      if (!isAuthenticated || !healthData) {
        throw new Error('Not authenticated or no data available');
      }
      await SecurityService.exportUserData('healthData');
      console.log('[MedicalContext] Data exported successfully');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to export health data';
      console.error('[MedicalContext] Error exporting health data:', err);
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const deleteData = async () => {
    console.log('[MedicalContext] Starting data deletion');
    try {
      setLoading(true);
      setError(null);
      if (!isAuthenticated) {
        throw new Error('Not authenticated');
      }
      await SecurityService.deleteUserData('healthData');
      setHealthData(null);
      console.log('[MedicalContext] Data deleted successfully');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete health data';
      console.error('[MedicalContext] Error deleting health data:', err);
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const clearHealthData = () => {
    console.log('[MedicalContext] Clearing health data from state');
    setHealthData(null);
    setError(null);
  };

  return (
    <MedicalContext.Provider
      value={{
        isAuthenticated,
        loading,
        healthData,
        error,
        authenticate,
        storeHealthData,
        exportData,
        deleteData,
        clearHealthData,
      }}
    >
      {children}
    </MedicalContext.Provider>
  );
}