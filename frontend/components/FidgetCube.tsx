import React, { useCallback } from 'react';

import { makeStyles } from '@rneui/themed';
import * as Haptics from 'expo-haptics';
import { StyleSheet, View, Platform, Pressable } from 'react-native';
import { PanGestureHandler } from 'react-native-gesture-handler';
import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withSpring,
  withSequence,
  withDecay,
  runOnJS,
  useAnimatedGestureHandler,
} from 'react-native-reanimated';

import { triggerImpactLight, triggerImpactMedium, triggerImpactHeavy, triggerSelection } from '../utils/haptics';

import type { ViewStyle } from 'react-native';
import type { PanGestureHandlerGestureEvent } from 'react-native-gesture-handler';



interface FidgetCubeProps {
  size?: number;
  primaryColor?: string;
  secondaryColor?: string;
  onInteraction?: (type: string, intensity: number) => void;
}

type GestureContext = {
  startX: number;
  startY: number;
  startRotateX: number;
  startRotateY: number;
};

const SPRING_CONFIG = {
  damping: 15,
  stiffness: 150,
  mass: 1,
};

const DECAY_CONFIG = {
  velocity: 0,
  deceleration: 0.997, // Higher value = longer spin
};

const ROTATION_FACTOR = 0.5; // Adjust this to control rotation sensitivity

interface FaceContent {
  type: 'click' | 'flip' | 'glide' | 'breathe' | 'roll' | 'spin';
  color: string;
}

// Add type for web-specific styles
interface WebStyles extends ViewStyle {
  transformStyle?: 'preserve-3d' | 'flat';
  transition?: string;
  backfaceVisibility?: 'visible' | 'hidden';
}

interface CubeStyles {
  container: ViewStyle;
  cube: ViewStyle;
  face: ViewStyle;
  faceContent: ViewStyle;
  facePattern: ViewStyle;
  clickFace: ViewStyle;
  button: ViewStyle;
  loudButton: ViewStyle;
  silentButton: ViewStyle;
  flipFace: ViewStyle;
  flipSwitch: ViewStyle;
  glideFace: ViewStyle;
  joystickBase: ViewStyle;
  joystick: ViewStyle;
  breatheFace: ViewStyle;
  worryStone: ViewStyle;
  rollFace: ViewStyle;
  gearContainer: ViewStyle;
  gear: ViewStyle;
  rollingBall: ViewStyle;
  spinFace: ViewStyle;
  dial: ViewStyle;
}

const SNAP_ANGLES = [-180, -90, 0, 90, 180];
const ROTATION_THRESHOLD = 45;

type FaceOrientation = {
  x: number;
  y: number;
};

type FaceOrientations = {
  [key in 'front' | 'back' | 'left' | 'right' | 'top' | 'bottom']: FaceOrientation;
};

// Define fixed orientations for each face
const FACE_ORIENTATIONS: FaceOrientations = {
  front: { x: 0, y: 0 },
  back: { x: 0, y: 180 },
  left: { x: 0, y: -90 },
  right: { x: 0, y: 90 },
  top: { x: -90, y: 0 },
  bottom: { x: 90, y: 0 }
};

const snapToNearestFace = (rotateX: number, rotateY: number) => {
  'worklet';
  // Normalize angles to -180 to 180 range
  const normalizedX = ((rotateX % 360 + 540) % 360) - 180;
  const normalizedY = ((rotateY % 360 + 540) % 360) - 180;

  // First determine if we're closer to a vertical rotation (top/bottom faces)
  const absX = Math.abs(normalizedX);
  const absY = Math.abs(normalizedY);

  if (absX > absY && absX > 45) {
    // We're looking more at top/bottom
    return {
      x: normalizedX > 0 ? 90 : -90, // Snap to straight top or bottom
      y: 0 // Reset Y rotation when showing top/bottom
    };
  } else {
    // We're looking at a side face
    // Reset X rotation for side views
    return {
      x: 0,
      y: Math.round(normalizedY / 90) * 90 // Snap to nearest 90° increment
    };
  }
};

const useStyles = makeStyles((theme) => ({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  cube: {
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
  face: {
    position: 'absolute',
    width: '100%',
    height: '100%',
    justifyContent: 'center',
    alignItems: 'center',
  },
  faceContent: {
    backgroundColor: theme.colors.text,
  },
  clickFace: {
    backgroundColor: theme.colors.secondary,
  },
  button: {
    width: 50,
    height: 50,
    borderRadius: theme.borderRadius.sm,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loudButton: {
    backgroundColor: theme.colors.error,
  },
  silentButton: {
    backgroundColor: theme.colors.success,
  },
  flipFace: {
    backgroundColor: theme.colors.warning,
  },
  flipSwitch: {
    width: 30,
    height: 10,
    backgroundColor: theme.colors.grey3,
  },
  glideFace: {
    backgroundColor: theme.colors.grey1,
  },
  joystickBase: {
    width: 60,
    height: 60,
    backgroundColor: theme.colors.grey2,
  },
  joystick: {
    width: 20,
    height: 20,
    backgroundColor: theme.colors.grey4,
  },
  breatheFace: {
    backgroundColor: theme.colors.grey5,
  },
  worryStone: {
    width: 40,
    height: 40,
    backgroundColor: theme.colors.greyOutline,
  },
  rollFace: {
    backgroundColor: theme.colors.grey0,
  },
  gearContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  gear: {
    width: 20,
    height: 20,
    backgroundColor: theme.colors.black,
  },
  rollingBall: {
    width: 15,
    height: 15,
    backgroundColor: theme.colors.white,
  },
  spinFace: {
    backgroundColor: theme.colors.primary,
  },
  dial: {
    width: 30,
    height: 30,
    backgroundColor: theme.colors.secondary,
  },
}));

export const FidgetCube: React.FC<FidgetCubeProps> = ({
  size = 200,
  primaryColor = '#4A90E2',
  secondaryColor = '#2E5C8A',
  onInteraction,
}) => {
  const styles = useStyles();
  // Animation values
  const rotateX = useSharedValue(0);
  const rotateY = useSharedValue(0);
  const scale = useSharedValue(1);
  const velocityX = useSharedValue(0);
  const velocityY = useSharedValue(0);
  const lastX = useSharedValue(0);
  const lastY = useSharedValue(0);
  const lastTime = useSharedValue(0);
  const isInteracting = useSharedValue(false);

  const triggerHaptic = useCallback((intensity: number) => {
    if (Platform.OS === 'web') return;

    if (intensity > 0.8) {
      triggerImpactHeavy();
    } else if (intensity > 0.5) {
      triggerImpactMedium();
    } else {
      triggerImpactLight();
    }
  }, []);

  const handleFacePress = (face: string) => {
    isInteracting.value = true;
    const intensity = Math.random();
    scale.value = withSequence(
      withSpring(0.95, SPRING_CONFIG),
      withSpring(1, SPRING_CONFIG)
    );

    // Stop any ongoing momentum
    velocityX.value = 0;
    velocityY.value = 0;

    // Rotate to show the pressed face
    switch (face) {
      case 'front':
        rotateX.value = withSpring(0, SPRING_CONFIG);
        rotateY.value = withSpring(0, SPRING_CONFIG);
        break;
      case 'back':
        rotateX.value = withSpring(0, SPRING_CONFIG);
        rotateY.value = withSpring(180, SPRING_CONFIG);
        break;
      case 'left':
        rotateX.value = withSpring(0, SPRING_CONFIG);
        rotateY.value = withSpring(-90, SPRING_CONFIG);
        break;
      case 'right':
        rotateX.value = withSpring(0, SPRING_CONFIG);
        rotateY.value = withSpring(90, SPRING_CONFIG);
        break;
      case 'top':
        rotateX.value = withSpring(-90, SPRING_CONFIG);
        rotateY.value = withSpring(0, SPRING_CONFIG);
        break;
      case 'bottom':
        rotateX.value = withSpring(90, SPRING_CONFIG);
        rotateY.value = withSpring(0, SPRING_CONFIG);
        break;
    }

    triggerHaptic(intensity);
    if (onInteraction) {
      onInteraction(face, intensity);
    }
  };

  const gestureHandler = useAnimatedGestureHandler<PanGestureHandlerGestureEvent, GestureContext>({
    onStart: (event, context) => {
      if (isInteracting.value) return;
      context.startX = event.x;
      context.startY = event.y;
      context.startRotateX = rotateX.value;
      context.startRotateY = rotateY.value;
    },
    onActive: (event, context) => {
      if (isInteracting.value) return;
      const deltaX = event.x - context.startX;
      const deltaY = event.y - context.startY;
      rotateY.value = context.startRotateY + deltaX * ROTATION_FACTOR;
      rotateX.value = context.startRotateX + deltaY * ROTATION_FACTOR;
    },
    onEnd: (event) => {
      if (isInteracting.value) {
        isInteracting.value = false;
        return;
      }

      const targetOrientation = snapToNearestFace(rotateX.value, rotateY.value);

      const springConfig = {
        damping: 15,
        stiffness: 300,
        mass: 1,
        restDisplacementThreshold: 0.01,
        restSpeedThreshold: 0.01,
        velocity: 0,
      };

      rotateX.value = withSpring(targetOrientation.x, springConfig);
      rotateY.value = withSpring(targetOrientation.y, springConfig);
    },
  });

  const cubeStyle = useAnimatedStyle(() => ({
    transform: [
      { perspective: 1200 },
      { scale: scale.value },
      { rotateX: `${rotateX.value}deg` },
      { rotateY: `${rotateY.value}deg` },
    ],
  }));

  const Face = ({ face, color, rotation, type }: { face: string; color: string; rotation: any[]; type: string }) => {
    const renderContent = () => {
      switch (type) {
        case 'click':
          return (
            <View style={styles.clickFace}>
              <Pressable style={[styles.button, styles.loudButton]} onPress={() => handleFacePress(face)} />
              <Pressable style={[styles.button, styles.loudButton]} onPress={() => handleFacePress(face)} />
              <Pressable style={[styles.button, styles.loudButton]} onPress={() => handleFacePress(face)} />
              <Pressable style={[styles.button, styles.silentButton]} onPress={() => handleFacePress(face)} />
              <Pressable style={[styles.button, styles.silentButton]} onPress={() => handleFacePress(face)} />
            </View>
          );
        case 'flip':
          return (
            <View style={styles.flipFace}>
              <Pressable style={styles.flipSwitch} onPress={() => handleFacePress(face)} />
            </View>
          );
        case 'glide':
          return (
            <View style={styles.glideFace}>
              <View style={styles.joystickBase}>
                <View style={styles.joystick} />
              </View>
            </View>
          );
        case 'breathe':
          return (
            <View style={styles.breatheFace}>
              <View style={styles.worryStone} />
            </View>
          );
        case 'roll':
          return (
            <View style={styles.rollFace}>
              <View style={styles.gearContainer}>
                <View style={styles.gear} />
                <View style={styles.gear} />
                <View style={styles.gear} />
              </View>
              <View style={styles.rollingBall} />
            </View>
          );
        case 'spin':
          return (
            <View style={styles.spinFace}>
              <View style={styles.dial} />
            </View>
          );
      }
    };

    return (
      <Animated.View
        style={[
          styles.face,
          {
            backgroundColor: color,
            transform: rotation,
            width: size,
            height: size,
          },
        ]}
      >
        <Pressable
          onPress={() => handleFacePress(face)}
          style={({ pressed }) => [
            styles.faceContent,
            { opacity: pressed ? 0.8 : 1 },
          ]}
        >
          {renderContent()}
        </Pressable>
      </Animated.View>
    );
  };

  const handleMouseDown = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    lastX.value = x;
    lastY.value = y;
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.buttons !== 1) return; // Only process when left mouse button is pressed

    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const deltaX = x - lastX.value;
    const deltaY = y - lastY.value;

    rotateY.value += deltaX * ROTATION_FACTOR;
    rotateX.value += deltaY * ROTATION_FACTOR;

    lastX.value = x;
    lastY.value = y;
  };

  const handleMouseUp = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const deltaX = x - lastX.value;
    const deltaY = y - lastY.value;

    const velocityMultiplier = 5; // Increased for web

    rotateX.value = withDecay({
      velocity: deltaY * velocityMultiplier,
      deceleration: 0.997,
    });

    rotateY.value = withDecay({
      velocity: deltaX * velocityMultiplier,
      deceleration: 0.997,
    });
  };

  if (Platform.OS === 'web') {
    return (
      <div
        style={{
          width: size * 1.5,
          height: size * 1.5,
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          cursor: 'grab',
          userSelect: 'none',
          touchAction: 'none',
          WebkitTouchCallout: 'none',
          WebkitUserSelect: 'none',
          KhtmlUserSelect: 'none',
          MozUserSelect: 'none',
          msUserSelect: 'none',
        }}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        <Animated.View style={[styles.cube, cubeStyle, { width: size, height: size }]}>
          <Face
            face="front"
            color={primaryColor}
            rotation={[{ translateZ: size / 2 }]}
            type="click"
          />
          <Face
            face="back"
            color={secondaryColor}
            rotation={[{ translateZ: -size / 2 }, { rotateY: '180deg' }]}
            type="flip"
          />
          <Face
            face="right"
            color={primaryColor}
            rotation={[{ translateX: size / 2 }, { rotateY: '90deg' }]}
            type="glide"
          />
          <Face
            face="left"
            color={secondaryColor}
            rotation={[{ translateX: -size / 2 }, { rotateY: '-90deg' }]}
            type="breathe"
          />
          <Face
            face="top"
            color={primaryColor}
            rotation={[{ translateY: -size / 2 }, { rotateX: '90deg' }]}
            type="roll"
          />
          <Face
            face="bottom"
            color={secondaryColor}
            rotation={[{ translateY: size / 2 }, { rotateX: '-90deg' }]}
            type="spin"
          />
        </Animated.View>
      </div>
    );
  }

  return (
    <View style={styles.container}>
      <Animated.View style={[styles.cube, cubeStyle, { width: size, height: size }]}>
        <Face
          face="front"
          color={primaryColor}
          rotation={[{ translateZ: size / 2 }]}
          type="click"
        />
        <Face
          face="back"
          color={secondaryColor}
          rotation={[{ translateZ: -size / 2 }, { rotateY: '180deg' }]}
          type="flip"
        />
        <Face
          face="right"
          color={primaryColor}
          rotation={[{ translateX: size / 2 }, { rotateY: '90deg' }]}
          type="glide"
        />
        <Face
          face="left"
          color={secondaryColor}
          rotation={[{ translateX: -size / 2 }, { rotateY: '-90deg' }]}
          type="breathe"
        />
        <Face
          face="top"
          color={primaryColor}
          rotation={[{ translateY: -size / 2 }, { rotateX: '90deg' }]}
          type="roll"
        />
        <Face
          face="bottom"
          color={secondaryColor}
          rotation={[{ translateY: size / 2 }, { rotateX: '-90deg' }]}
          type="spin"
        />
      </Animated.View>
    </View>
  );
};

const styles = StyleSheet.create<CubeStyles>({
  container: {
    justifyContent: 'center',
    alignItems: 'center',
    ...(Platform.OS === 'web' ? {
      cursor: 'grab',
      userSelect: 'none',
      touchAction: 'none',
    } : {}),
  },
  cube: {
    position: 'relative',
    ...(Platform.OS === 'web' ? {
      transformStyle: 'preserve-3d',
      transition: 'transform 0.2s ease-out',
    } : {}),
  },
  face: {
    position: 'absolute',
    width: '100%',
    height: '100%',
    ...(Platform.OS === 'web' ? {
      backfaceVisibility: 'hidden',
    } : {}),
    borderWidth: 1,
    borderColor: 'rgba(0,0,0,0.1)',
    overflow: 'hidden',
  },
  faceContent: {
    width: '100%',
    height: '100%',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  facePattern: {
    width: '60%',
    height: '60%',
    borderRadius: 15,
    opacity: 0.8,
  },
  clickFace: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-around',
    padding: 10,
  },
  button: {
    width: '30%',
    height: '30%',
    borderRadius: 15,
    margin: 5,
  },
  loudButton: {
    backgroundColor: '#2E5C8A',
    elevation: 3,
  },
  silentButton: {
    backgroundColor: '#4A90E2',
    opacity: 0.7,
  },
  flipFace: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  flipSwitch: {
    width: '60%',
    height: 30,
    backgroundColor: '#2E5C8A',
    borderRadius: 15,
  },
  glideFace: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  joystickBase: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#2E5C8A',
    alignItems: 'center',
    justifyContent: 'center',
  },
  joystick: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#4A90E2',
  },
  breatheFace: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  worryStone: {
    width: '80%',
    height: '60%',
    borderRadius: 30,
    backgroundColor: '#2E5C8A',
    opacity: 0.8,
  },
  rollFace: {
    alignItems: 'center',
    justifyContent: 'space-around',
  },
  gearContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    width: '100%',
  },
  gear: {
    width: 30,
    height: 30,
    borderRadius: 15,
    backgroundColor: '#2E5C8A',
  },
  rollingBall: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#4A90E2',
  },
  spinFace: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  dial: {
    width: '70%',
    height: '70%',
    borderRadius: 100,
    backgroundColor: '#2E5C8A',
    borderWidth: 5,
    borderColor: '#4A90E2',
  },
});
