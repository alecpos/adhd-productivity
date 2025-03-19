import { Text } from '@rneui/themed';
import { makeStyles, useTheme } from '@rneui/themed';

import type { TextProps } from '@rneui/base';

export function MonoText(props: TextProps) {
  const styles = useStyles();
  return <Text {...props} style={[styles.monoText, props.style]} />;
}

const useStyles = makeStyles((theme) => ({
  monoText: {
    fontFamily: 'SpaceMono',
    color: theme.colors.text
  }
}));
