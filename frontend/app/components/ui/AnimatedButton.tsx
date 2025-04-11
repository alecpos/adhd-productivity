import React from 'react';

import { Button, Icon } from '@rneui/themed';
import { TouchableOpacity, StyleSheet, Animated, View, Text } from 'react-native';

import type { IconNode } from '@rneui/base';
import type { ButtonProps, IconProps } from '@rneui/themed';

interface AnimatedButtonProps extends Omit<ButtonProps, 'TouchableComponent'> {
  scaleOnPress?: boolean;
  icon?: IconNode;
}

export function AnimatedButton({ scaleOnPress = true, ...props }: AnimatedButtonProps) {
  const scaleAnim = React.useRef(new Animated.Value(1)).current;

  const handlePressIn = () => {
    if (scaleOnPress) {
      Animated.spring(scaleAnim, {
        toValue: 0.95,
        useNativeDriver: true,
      }).start();
    }
  };

  const handlePressOut = () => {
    if (scaleOnPress) {
      Animated.spring(scaleAnim, {
        toValue: 1,
        useNativeDriver: true,
      }).start();
    }
  };

  const {
    onPress,
    disabled,
    icon,
    title,
    titleStyle,
    buttonStyle,
    containerStyle,
    iconPosition = 'left',
    iconRight = false,
    ...otherProps
  } = props;

  const renderIcon = () => {
    if (!icon) return null;

    if (React.isValidElement(icon)) {
      return icon;
    }

    const iconProps = typeof icon === 'object' ? icon : { name: icon };
    return (
      <Icon
        {...(iconProps as IconProps)}
        containerStyle={[
          styles.iconContainer,
          iconPosition === 'right' || iconRight ? styles.iconRight : styles.iconLeft,
        ]}
      />
    );
  };

  return (
    <TouchableOpacity
      onPressIn={handlePressIn}
      onPressOut={handlePressOut}
      style={[{ opacity: disabled ? 0.5 : 1 }, containerStyle]}
      disabled={disabled}
      onPress={onPress}
      {...otherProps}
    >
      <Animated.View style={[{ transform: [{ scale: scaleAnim }] }, buttonStyle]}>
        <View style={styles.contentContainer}>
          {iconPosition === 'left' && !iconRight && renderIcon()}
          {typeof title === 'string' ? (
            <Text style={titleStyle}>{title}</Text>
          ) : (
            title
          )}
          {(iconPosition === 'right' || iconRight) && renderIcon()}
        </View>
      </Animated.View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  contentContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 12,
  },
  iconContainer: {
    marginHorizontal: 8,
  },
  iconLeft: {
    marginRight: 8,
    marginLeft: 0,
  },
  iconRight: {
    marginLeft: 8,
    marginRight: 0,
  },
});
