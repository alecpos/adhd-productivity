import { Text as RNEText } from '@rneui/themed';
import { View as RNView } from 'react-native';

import type { TextProps as RNETextProps } from '@rneui/themed';
import type { ViewProps as RNViewProps } from 'react-native';

export type TextProps = RNETextProps;
export type ViewProps = RNViewProps;

export function Text(props: TextProps) {
  return <RNEText {...props} />;
}

export function View(props: ViewProps) {
  return <RNView {...props} />;
}

export { useTheme } from '@rneui/themed'; 