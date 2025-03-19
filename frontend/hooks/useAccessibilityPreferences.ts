import { useState, useEffect } from 'react';
import { AccessibilityInfo } from 'react-native';

interface AccessibilityPreferences {
  reduceMotion: boolean;
  highContrast: boolean;
  screenReaderEnabled: boolean;
  fontScale: number;
}

export const useAccessibilityPreferences = (): AccessibilityPreferences => {
  const [reduceMotion, setReduceMotion] = useState(false);
  const [highContrast, setHighContrast] = useState(false);
  const [screenReaderEnabled, setScreenReaderEnabled] = useState(false);
  const [fontScale, setFontScale] = useState(1);

  useEffect(() => {
    // Check if reduce motion is enabled
    AccessibilityInfo.isReduceMotionEnabled().then(
      (isReduceMotionEnabled) => {
        setReduceMotion(isReduceMotionEnabled);
      }
    );

    // Subscribe to reduce motion changes
    const reduceMotionListener = AccessibilityInfo.addEventListener(
      'reduceMotionChanged',
      setReduceMotion
    );

    // Check if screen reader is enabled
    AccessibilityInfo.isScreenReaderEnabled().then(
      (isScreenReaderEnabled) => {
        setScreenReaderEnabled(isScreenReaderEnabled);
      }
    );

    // Subscribe to screen reader changes
    const screenReaderListener = AccessibilityInfo.addEventListener(
      'screenReaderChanged',
      setScreenReaderEnabled
    );

    // Get font scale if available
    if (AccessibilityInfo.getRecommendedFontSizes) {
      AccessibilityInfo.getRecommendedFontSizes().then(
        (sizes) => {
          if (sizes && sizes.headline) {
            setFontScale(sizes.headline / 24); // Assuming headline base size is 24
          }
        }
      );
    }

    // Cleanup listeners
    return () => {
      reduceMotionListener.remove();
      screenReaderListener.remove();
    };
  }, []);

  return {
    reduceMotion,
    highContrast, // This would ideally come from system settings but React Native doesn't expose this directly
    screenReaderEnabled,
    fontScale,
  };
}; 