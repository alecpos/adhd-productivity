import React from 'react';

import { Text, useTheme, makeStyles } from '@rneui/themed';
import LottieView from 'lottie-react-native';
import { View, Dimensions } from 'react-native';

export interface LoadingAnimationProps {
  text?: string;
  fullScreen?: boolean;
  overlay?: boolean;
  size?: number;
  source?: any; // Can be a local require() or a remote URI
}

const defaultAnimation = require('../../assets/animations/loading.json');
const { width } = Dimensions.get('window');

export const LoadingAnimation: React.FC<LoadingAnimationProps> = ({
  text,
  fullScreen = false,
  overlay = false,
  size = width * 0.3, // 30% of screen width by default
  source = defaultAnimation,
}) => {
  const { theme } = useTheme();
  const styles = useStyles();

  const containerStyle = [
    styles.container,
    fullScreen && styles.fullScreen,
    overlay && [styles.overlay, { backgroundColor: `${theme.colors.black}CC` }],
  ];

  const animationStyle = {
    width: size,
    height: size,
  };

  return (
    <View style={containerStyle}>
      <LottieView
        source={source}
        autoPlay
        loop
        style={animationStyle}
      />
      {text && (
        <Text
          style={[styles.text]}
          h4
        >
          {text}
        </Text>
      )}
    </View>
  );
};

const useStyles = makeStyles((theme) => ({
  container: {
    padding: theme.spacing.lg,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: theme.borderRadius.md,
  },
  fullScreen: {
    flex: 1,
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'transparent',
    zIndex: 999,
  },
  overlay: {
    backgroundColor: `${theme.colors.black}B3`, // 70% opacity
  },
  text: {
    marginTop: theme.spacing.md,
    textAlign: 'center',
    color: theme.colors.text,
  },
}));