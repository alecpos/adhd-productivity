import { useColorScheme } from 'react-native';

interface ThemeColors {
  primary: string;
  secondary: string;
  background: string;
  surface: string;
  text: string;
  textSecondary: string;
  border: string;
  error: string;
  success: string;
  warning: string;
  info: string;
}

interface Theme {
  colors: ThemeColors;
  isDark: boolean;
}

const lightColors: ThemeColors = {
  primary: '#007AFF',
  secondary: '#5856D6',
  background: '#FFFFFF',
  surface: '#F2F2F7',
  text: '#000000',
  textSecondary: '#6C6C6C',
  border: '#C6C6C8',
  error: '#FF3B30',
  success: '#34C759',
  warning: '#FF9500',
  info: '#5856D6',
};

const darkColors: ThemeColors = {
  primary: '#0A84FF',
  secondary: '#5E5CE6',
  background: '#000000',
  surface: '#1C1C1E',
  text: '#FFFFFF',
  textSecondary: '#8E8E93',
  border: '#38383A',
  error: '#FF453A',
  success: '#32D74B',
  warning: '#FF9F0A',
  info: '#5E5CE6',
};

export const useTheme = (): Theme => {
  const colorScheme = useColorScheme();
  const isDark = colorScheme === 'dark';
  const colors = isDark ? darkColors : lightColors;

  return {
    colors,
    isDark,
  };
};
