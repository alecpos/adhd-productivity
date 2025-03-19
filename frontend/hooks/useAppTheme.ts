import { useTheme, makeStyles } from '@rneui/themed';

export const useAppTheme = () => {
  const { theme } = useTheme();
  return theme;
};

export const createThemedStyle = makeStyles; 