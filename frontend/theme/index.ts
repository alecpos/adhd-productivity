import { useTheme as useRNETheme } from '@rneui/themed';

// Re-export the useTheme hook for consistent usage throughout the app
export const useTheme = () => {
  const { theme } = useRNETheme();
  
  return {
    theme: {
      colors: {
        primary: '#4782DA',
        secondary: '#47A6DA',
        background: '#FFFFFF',
        surface: '#F5F5F5',
        error: '#DA4747',
        text: '#333333',
        grey5: '#E0E0E0',
        grey3: '#AAAAAA',
        grey1: '#666666',
        // Add any other colors you need from the theme
      },
      dark: false,
      // Add any other theme properties you might need
    }
  };
}; 