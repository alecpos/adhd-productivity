import { createTheme, useTheme } from '@rneui/themed';

import type { Theme } from '@rneui/themed';
import type { TextStyle, ViewStyle } from 'react-native';

declare module '@rneui/themed' {
  export interface Colors {
    text: string;
    surface: string;
    border: string;
  }
  
  export interface Theme {
    fontSize: {
      xs: number;
      sm: number;
      md: number;
      lg: number;
      xl: number;
    };
    spacing: {
      xs: number;
      sm: number;
      md: number;
      lg: number;
      xl: number;
    };
    borderRadius: {
      xs: number;
      sm: number;
      md: number;
      lg: number;
    };
    shadows: {
      sm: ViewStyle;
      md: ViewStyle;
      lg: ViewStyle;
    };
  }
}

export const theme = createTheme({
  lightColors: {
    primary: '#4CAF50',
    secondary: '#03A9F4',
    background: '#FFFFFF',
    text: '#212121',
    error: '#F44336',
    white: '#FFFFFF',
    black: '#212121',
    grey0: '#393e42',
    grey1: '#43484d',
    grey2: '#5e6977',
    grey3: '#86939e',
    grey4: '#bdc6cf',
    grey5: '#e1e8ee',
    greyOutline: '#bbb',
    success: '#52c41a',
    warning: '#faad14',
    disabled: 'hsl(208, 8%, 90%)',
  },
  darkColors: {
    primary: '#81C784',
    secondary: '#4FC3F7',
    background: '#212121',
    text: '#E0E0E0',
    error: '#FF5252',
    white: '#FFFFFF',
    black: '#212121',
    grey0: '#d9d9d9',
    grey1: '#bfbfbf',
    grey2: '#999999',
    grey3: '#808080',
    grey4: '#666666',
    grey5: '#4d4d4d',
    greyOutline: '#595959',
    success: '#52c41a',
    warning: '#faad14',
    disabled: 'hsl(208, 8%, 90%)',
  },
  mode: 'light',
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
  },
  fontSize: {
    xs: 12,
    sm: 14,
    md: 16,
    lg: 18,
    xl: 20,
  },
  components: {
    Button: {
      raised: true,
      buttonStyle: {
        borderRadius: 8,
        padding: 16,
      } as ViewStyle,
    },
    Input: {
      containerStyle: {
        marginVertical: 8,
      } as ViewStyle,
      inputStyle: {
        paddingLeft: 8,
        fontSize: 16,
      } as TextStyle,
    },
    Text: {
      h1Style: {
        fontSize: 32,
        fontWeight: 'bold',
        color: '#212121',
      } as TextStyle,
      h2Style: {
        fontSize: 28,
        fontWeight: 'bold',
        color: '#212121',
      } as TextStyle,
      h3Style: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#212121',
      } as TextStyle,
      h4Style: {
        fontSize: 20,
        fontWeight: 'bold',
        color: '#212121',
      } as TextStyle,
    },
    Card: {
      containerStyle: {
        borderRadius: 8,
        padding: 16,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
      } as ViewStyle,
    },
    ListItem: {
      containerStyle: {
        borderRadius: 4,
        marginVertical: 4,
      } as ViewStyle,
    },
    Icon: {
      size: 24,
      color: '#4CAF50',
    },
  },
});

// Custom hook to use our themed styles
export const useAppTheme = (): Theme => {
  const { theme: currentTheme } = useTheme();
  return currentTheme as Theme;
};

// Type-safe theme access
export type AppTheme = typeof theme; 