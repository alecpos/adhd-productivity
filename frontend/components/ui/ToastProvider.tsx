import React, { createContext, useContext, useCallback } from 'react';

import Toast from 'react-native-toast-message';

type ToastType = 'success' | 'error' | 'info';

interface ToastParams {
  type: ToastType;
  message: string;
  duration?: number;
}

interface ToastContextType {
  showToast: (params: ToastParams) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const showToast = useCallback(({ type, message, duration = 3000 }: ToastParams) => {
    Toast.show({
      type,
      text1: type.charAt(0).toUpperCase() + type.slice(1),
      text2: message,
      visibilityTime: duration,
      position: 'bottom',
    });
  }, []);

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      <Toast />
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (context === undefined) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
} 