import React, { useEffect } from 'react';

import { makeStyles } from '@rneui/themed';
import * as Haptics from 'expo-haptics';
import { StyleSheet, View, Platform, Pressable } from 'react-native';
import { PanGestureHandler } from 'react-native-gesture-handler';
import Animated, {
  useAnimatedGestureHandler,
  useAnimatedStyle,
  useSharedValue,
  withDecay,
  withSpring,
  runOnJS,
  interpolate,
} from 'react-native-reanimated';

import { triggerImpactLight, triggerImpactMedium, triggerImpactHeavy } from '../utils/haptics';

import type { PanGestureHandlerGestureEvent } from 'react-native-gesture-handler';




interface FidgetSpinnerProps {
  size?: number;
  primaryColor?: string;
  secondaryColor?: string;
  onSpinComplete?: (speed: number) => void;
}

interface WebMouseEvent {
  nativeEvent: {
    offsetX: number;
    offsetY: number;
    buttons: number;
  };
}

type ContextType = {
  startX: number;
  startY: number;
  lastRotation: number;
};

const FRICTION = 0.95; // Increased friction (was 0.98)
const ELASTICITY = 0.7; // Bounce factor when hitting rotation limits
const MIN_VELOCITY_THRESHOLD = 0.1;
const SENSITIVITY = 0.5; // New sensitivity multiplier

const useStyles = makeStyles((theme) => ({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  spinner: {
    width: 200,
    height: 200,
    backgroundColor: theme.colors.primary,
    borderRadius: theme.borderRadius.md,
    shadowColor: theme.colors.black,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  handle: {
    width: 50,
    height: 50,
    backgroundColor: theme.colors.secondary,
    borderRadius: theme.borderRadius.sm,
    justifyContent: 'center',
    alignItems: 'center',
  },
}));

export const FidgetSpinner: React.FC<FidgetSpinnerProps> = ({
  size = 200,
  primaryColor = '#4A90E2',
  secondaryColor = '#2E5C8A',
  onSpinComplete,
}) => {
  const styles = useStyles();
  const rotation = useSharedValue(0);
  const velocity = useSharedValue(0);
  const lastTime = useSharedValue(0);
  const isSpinning = useSharedValue(false);
  const dragStart = useSharedValue({ x: 0, y: 0 });
  const lastAngle = useSharedValue(0);

  const calculateAngle = (x: number, y: number, centerX: number, centerY: number) => {
    return Math.atan2(y - centerY, x - centerX) * (180 / Math.PI);
  };

  const updateSpinnerPhysics = () => {
    'worklet';
    if (!isSpinning.value || Math.abs(velocity.value) < MIN_VELOCITY_THRESHOLD) {
      isSpinning.value = false;
      return;
    }

    const now = Date.now();
    const deltaTime = now - lastTime.value;
    lastTime.value = now;

    // Apply friction
    velocity.value *= Math.pow(FRICTION, deltaTime / 16);
    rotation.value += velocity.value * (deltaTime / 16);

    // Request next frame if still spinning
    if (Math.abs(velocity.value) >= MIN_VELOCITY_THRESHOLD) {
      requestAnimationFrame(updateSpinnerPhysics);
    } else {
      isSpinning.value = false;
    }
  };

  const gestureHandler = useAnimatedGestureHandler<
    PanGestureHandlerGestureEvent,
    ContextType
  >({
    onStart: (event, context) => {
      context.startX = event.x;
      context.startY = event.y;
      context.lastRotation = rotation.value;
      isSpinning.value = false;
      dragStart.value = { x: event.x, y: event.y };
      lastAngle.value = calculateAngle(event.x, event.y, size / 2, size / 2);
    },
    onActive: (event, context) => {
      const currentAngle = calculateAngle(event.x, event.y, size / 2, size / 2);
      let deltaAngle = currentAngle - lastAngle.value;

      if (deltaAngle > 180) deltaAngle -= 360;
      if (deltaAngle < -180) deltaAngle += 360;

      rotation.value = context.lastRotation + (deltaAngle * SENSITIVITY);
      velocity.value = deltaAngle * SENSITIVITY; // Reduced sensitivity

      if (Math.abs(velocity.value) > 200) {
        runOnJS(triggerHaptic)(Math.abs(velocity.value));
      }

      lastAngle.value = currentAngle;
    },
    onEnd: (event) => {
      isSpinning.value = true;
      lastTime.value = Date.now();
      requestAnimationFrame(updateSpinnerPhysics);

      if (onSpinComplete) {
        runOnJS(onSpinComplete)(Math.abs(velocity.value));
      }
    },
  });

  const triggerHaptic = (speed: number) => {
    if (Platform.OS === 'web') return;

    if (speed > 800) {
      triggerImpactHeavy();
    } else if (speed > 400) {
      triggerImpactMedium();
    } else if (speed > 200) {
      triggerImpactLight();
    }
  };

  const animatedStyle = useAnimatedStyle(() => {
    return {
      transform: [
        { rotate: `${rotation.value}deg` },
        { scale: interpolate(Math.abs(velocity.value), [0, 1000], [1, 1.05]) }
      ],
    };
  });

  const SpinnerContent = () => (
    <Animated.View style={[styles.spinner, animatedStyle]}>
      <View style={[styles.handle, { backgroundColor: primaryColor }]} />
      <View style={[styles.handle, { backgroundColor: secondaryColor, transform: [{ rotate: '120deg' }] }]} />
      <View style={[styles.handle, { backgroundColor: primaryColor, transform: [{ rotate: '240deg' }] }]} />
      <View style={[styles.handle, { backgroundColor: secondaryColor }]} />
    </Animated.View>
  );

  if (Platform.OS === 'web') {
    return (
      <View
        style={[styles.container, { touchAction: 'none' } as any]}
        onStartShouldSetResponder={() => true}
        onMoveShouldSetResponder={() => true}
        onResponderGrant={(e: any) => {
          e.preventDefault();
          e.stopPropagation();
          const rect = (e.target as HTMLElement).getBoundingClientRect();
          const x = e.nativeEvent.pageX - rect.left;
          const y = e.nativeEvent.pageY - rect.top;
          dragStart.value = { x, y };
          lastAngle.value = calculateAngle(x, y, size / 2, size / 2);
          isSpinning.value = false;
        }}
        onResponderMove={(e: any) => {
          e.preventDefault();
          e.stopPropagation();
          const rect = (e.target as HTMLElement).getBoundingClientRect();
          const x = e.nativeEvent.pageX - rect.left;
          const y = e.nativeEvent.pageY - rect.top;
          const currentAngle = calculateAngle(x, y, size / 2, size / 2);
          let deltaAngle = currentAngle - lastAngle.value;

          if (deltaAngle > 180) deltaAngle -= 360;
          if (deltaAngle < -180) deltaAngle += 360;

          rotation.value += deltaAngle * SENSITIVITY;
          velocity.value = deltaAngle * SENSITIVITY;
          lastAngle.value = currentAngle;
        }}
        onResponderRelease={(e: any) => {
          e.preventDefault();
          e.stopPropagation();
          isSpinning.value = true;
          lastTime.value = Date.now();
          requestAnimationFrame(updateSpinnerPhysics);
        }}
      >
        <SpinnerContent />
      </View>
    );
  }

  return (
    <PanGestureHandler onGestureEvent={gestureHandler}>
      <Animated.View style={styles.container}>
        <SpinnerContent />
      </Animated.View>
    </PanGestureHandler>
  );
};
