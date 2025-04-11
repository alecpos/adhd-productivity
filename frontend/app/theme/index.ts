import { createTheme } from '@rneui/themed';

import type { CustomTheme } from '../types/theme';

export const theme = createTheme({
  lightColors: {
    primary: '#4B6BF5',  // Modern blue
    secondary: '#9747FF', // Purple
    background: '#F5F7FF',
    surface: '#FFFFFF',
    text: '#1A1F36',
    border: '#E1E5F2',
    grey0: '#1A1F36',
    grey1: '#3C4257',
    grey2: '#697386',
    grey3: '#8792A2',
    grey4: '#C1C9D2',
    grey5: '#E3E8EF',
  },
  darkColors: {
    primary: '#4B6BF5',
    secondary: '#9747FF',
    background: '#1A1F36',
    surface: '#252D43',
    text: '#F5F7FF',
    border: '#3C4257',
    grey0: '#E3E8EF',
    grey1: '#C1C9D2',
    grey2: '#8792A2',
    grey3: '#697386',
    grey4: '#3C4257',
    grey5: '#1A1F36',
  },
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
  borderRadius: {
    xs: 4,
    sm: 8,
    md: 12,
    lg: 16,
  },
  shadows: {
    sm: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 1 },
      shadowOpacity: 0.18,
      shadowRadius: 1.0,
      elevation: 1,
    },
    md: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.25,
      shadowRadius: 3.84,
      elevation: 5,
    },
    lg: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.30,
      shadowRadius: 4.65,
      elevation: 8,
    },
  },
  components: {
    Card: {
      containerStyle: {
        borderRadius: 16,
        shadowColor: '#000',
        shadowOpacity: 0.1,
        elevation: 3,
      }
    },
    Button: {
      raised: true,
      buttonStyle: {
        borderRadius: 12,
        paddingVertical: 12,
      },
    },
    Input: {
      containerStyle: {
        paddingHorizontal: 0,
      },
    },
  },
}) as CustomTheme;
