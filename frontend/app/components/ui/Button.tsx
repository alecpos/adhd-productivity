import React from 'react';

import { Button as RNEButton, makeStyles, useTheme } from '@rneui/themed';
import { ActivityIndicator, Platform } from 'react-native';

import type { ButtonProps as RNEButtonProps} from '@rneui/themed';

type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
type ButtonSize = 'small' | 'medium' | 'large';

interface ButtonProps extends Omit<RNEButtonProps, 'title' | 'type' | 'size'> {
  title: string;
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
  loadingText?: string;
  fullWidth?: boolean;
  icon?: React.ReactElement;
  iconPosition?: 'left' | 'right';
}

export const Button: React.FC<ButtonProps> = ({ 
  title,
  variant = 'primary',
  size = 'medium',
  isLoading = false,
  loadingText,
  fullWidth = false,
  icon,
  iconPosition = 'left',
  disabled,
  ...props 
}) => {
  const { theme } = useTheme();
  const styles = useStyles();

  const getVariantStyles = () => {
    const variants = {
      primary: {
        backgroundColor: theme.colors.primary,
        buttonStyle: styles.primaryButton,
        titleStyle: styles.primaryTitle,
      },
      secondary: {
        backgroundColor: theme.colors.secondary,
        buttonStyle: styles.secondaryButton,
        titleStyle: styles.secondaryTitle,
      },
      outline: {
        type: 'outline' as const,
        buttonStyle: styles.outlineButton,
        titleStyle: styles.outlineTitle,
      },
      ghost: {
        type: 'clear' as const,
        buttonStyle: styles.ghostButton,
        titleStyle: styles.ghostTitle,
      },
      danger: {
        backgroundColor: theme.colors.error,
        buttonStyle: styles.dangerButton,
        titleStyle: styles.dangerTitle,
      },
    };
    return variants[variant];
  };

  const getSizeStyles = () => {
    const sizes = {
      small: styles.smallButton,
      medium: styles.mediumButton,
      large: styles.largeButton,
    };
    return sizes[size];
  };

  const renderIcon = () => {
    if (!icon) return undefined;
    return React.cloneElement(icon, {
      size: size === 'small' ? 16 : size === 'medium' ? 20 : 24,
      color: variant === 'outline' || variant === 'ghost' 
        ? theme.colors.primary 
        : theme.colors.white,
      style: iconPosition === 'right' ? { marginLeft: 8 } : { marginRight: 8 }
    });
  };

  const variantStyles = getVariantStyles();
  const sizeStyles = getSizeStyles();

  return (
    <RNEButton
      {...variantStyles}
      {...props}
      disabled={disabled || isLoading}
      loading={isLoading}
      loadingProps={{
        size: size === 'small' ? 'small' : 'large',
        color: variant === 'outline' || variant === 'ghost' 
          ? theme.colors.primary 
          : theme.colors.white
      }}
      loadingStyle={styles.loadingStyle}
      title={isLoading ? loadingText || title : title}
      containerStyle={[
        styles.container,
        fullWidth && styles.fullWidth,
        props.containerStyle,
      ]}
      buttonStyle={[
        variantStyles.buttonStyle,
        sizeStyles,
        disabled && styles.disabledButton,
        props.buttonStyle,
      ]}
      titleStyle={[
        variantStyles.titleStyle,
        disabled && styles.disabledTitle,
        props.titleStyle,
      ]}
      icon={renderIcon()}
      iconRight={iconPosition === 'right'}
    />
  );
};

const useStyles = makeStyles((theme) => ({
  container: {
    borderRadius: 8,
    overflow: 'hidden',
    ...Platform.select({
      ios: {
        shadowColor: theme.colors.grey3,
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.25,
        shadowRadius: 3.84,
      },
      android: {
        elevation: 3,
      },
    }),
  },
  fullWidth: {
    width: '100%',
  },
  // Button Variants
  primaryButton: {
    borderRadius: 8,
    backgroundColor: theme.colors.primary,
  },
  secondaryButton: {
    borderRadius: 8,
    backgroundColor: theme.colors.secondary,
  },
  outlineButton: {
    borderRadius: 8,
    borderWidth: 2,
    borderColor: theme.colors.primary,
  },
  ghostButton: {
    borderRadius: 8,
    backgroundColor: 'transparent',
  },
  dangerButton: {
    borderRadius: 8,
    backgroundColor: theme.colors.error,
  },
  // Title Variants
  primaryTitle: {
    color: theme.colors.white,
    fontWeight: '600',
  },
  secondaryTitle: {
    color: theme.colors.white,
    fontWeight: '600',
  },
  outlineTitle: {
    color: theme.colors.primary,
    fontWeight: '600',
  },
  ghostTitle: {
    color: theme.colors.primary,
    fontWeight: '600',
  },
  dangerTitle: {
    color: theme.colors.white,
    fontWeight: '600',
  },
  // Button Sizes
  smallButton: {
    paddingVertical: 8,
    paddingHorizontal: 16,
  },
  mediumButton: {
    paddingVertical: 12,
    paddingHorizontal: 24,
  },
  largeButton: {
    paddingVertical: 16,
    paddingHorizontal: 32,
  },
  // States
  disabledButton: {
    backgroundColor: theme.colors.disabled,
    borderColor: theme.colors.disabled,
  },
  disabledTitle: {
    color: theme.colors.grey3,
  },
  loadingStyle: {
    marginRight: 8,
  },
}));

export default Button; 