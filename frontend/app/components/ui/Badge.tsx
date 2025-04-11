import React from 'react';

import { Badge as RNEBadge, makeStyles, useTheme, Text } from '@rneui/themed';
import { View } from 'react-native';

import type { BadgeProps as RNEBadgeProps} from '@rneui/themed';

type BadgeVariant = 'solid' | 'outline' | 'dot';
type BadgeSize = 'small' | 'medium' | 'large';
type BadgeStatus = 'primary' | 'success' | 'warning' | 'error' | 'info';

interface BadgeProps extends Omit<RNEBadgeProps, 'status'> {
  variant?: BadgeVariant;
  size?: BadgeSize;
  status?: BadgeStatus;
  label?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  variant = 'solid',
  size = 'medium',
  status = 'primary',
  label,
  ...props
}) => {
  const { theme } = useTheme();
  const styles = useStyles();

  const getVariantStyles = () => {
    const variants = {
      solid: {
        badgeStyle: styles.solidBadge,
        textStyle: styles.solidText,
      },
      outline: {
        badgeStyle: styles.outlineBadge,
        textStyle: styles.outlineText,
      },
      dot: {
        badgeStyle: styles.dotBadge,
        textStyle: {},
      },
    };
    return variants[variant];
  };

  const getSizeStyles = () => {
    const sizes = {
      small: styles.smallBadge,
      medium: styles.mediumBadge,
      large: styles.largeBadge,
    };
    return sizes[size];
  };

  const getStatusColor = () => {
    const colors = {
      primary: theme.colors.primary,
      success: theme.colors.success,
      warning: theme.colors.warning,
      error: theme.colors.error,
      info: theme.colors.secondary,
    };
    return colors[status];
  };

  if (variant === 'dot') {
    return (
      <View style={[
        styles.dotBadge,
        getSizeStyles(),
        { backgroundColor: getStatusColor() },
      ]} />
    );
  }

  return (
    <RNEBadge
      badgeStyle={[
        getVariantStyles().badgeStyle,
        getSizeStyles(),
        variant === 'solid' && { backgroundColor: getStatusColor() },
        variant === 'outline' && { borderColor: getStatusColor() },
      ]}
      textStyle={[
        getVariantStyles().textStyle,
        variant === 'outline' && { color: getStatusColor() },
      ]}
      value={label}
      {...props}
    />
  );
};

const useStyles = makeStyles((theme) => ({
  // Variant Styles
  solidBadge: {
    borderRadius: 16,
    paddingHorizontal: 8,
  },
  solidText: {
    color: theme.colors.white,
    fontSize: 12,
    fontWeight: '600',
  },
  outlineBadge: {
    borderRadius: 16,
    paddingHorizontal: 8,
    backgroundColor: 'transparent',
    borderWidth: 1,
  },
  outlineText: {
    fontSize: 12,
    fontWeight: '600',
  },
  dotBadge: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  // Size Styles
  smallBadge: {
    minWidth: 16,
    height: 16,
    paddingHorizontal: 4,
  },
  mediumBadge: {
    minWidth: 20,
    height: 20,
    paddingHorizontal: 6,
  },
  largeBadge: {
    minWidth: 24,
    height: 24,
    paddingHorizontal: 8,
  },
}));

export default Badge;
