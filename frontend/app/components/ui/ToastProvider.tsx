import React, { createContext, useContext, useCallback, useState } from 'react';

import Toast from './Toast';

type ToastType = 'success' | 'error' | 'warning' | 'info';
type ToastPosition = 'top' | 'bottom';

interface ToastConfig {
  type?: ToastType;
  message: string;
  position?: ToastPosition;
  duration?: number;
  action?: {
    label: string;
    onPress: () => void;
  };
}

interface ToastContextValue {
  showToast: (config: ToastConfig) => void;
  hideToast: () => void;
}

const ToastContext = createContext<ToastContextValue | undefined>(undefined);

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

interface ToastProviderProps {
  children: React.ReactNode;
}

export const ToastProvider: React.FC<ToastProviderProps> = ({ children }) => {
  const [toast, setToast] = useState<{
    visible: boolean;
    config: ToastConfig | null;
  }>({
    visible: false,
    config: null,
  });

  const showToast = useCallback((config: ToastConfig) => {
    setToast({
      visible: true,
      config,
    });
  }, []);

  const hideToast = useCallback(() => {
    setToast((prev) => ({
      ...prev,
      visible: false,
    }));
  }, []);

  return (
    <ToastContext.Provider value={{ showToast, hideToast }}>
      {children}
      {toast.config && (
        <Toast
          visible={toast.visible}
          type={toast.config.type}
          message={toast.config.message}
          position={toast.config.position}
          duration={toast.config.duration}
          action={toast.config.action}
          onClose={hideToast}
        />
      )}
    </ToastContext.Provider>
  );
};

export default ToastProvider; 