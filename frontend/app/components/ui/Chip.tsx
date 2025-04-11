import React from 'react';

import { ButtonProps } from '@rneui/base';
import { Chip as RNEChip, makeStyles, useTheme } from '@rneui/themed';
import { Pressable } from 'react-native';

import type { RneFunctionComponent } from '@rneui/base';
import type { ChipProps as RNEChipProps } from '@rneui/base/dist/Chip/Chip';

type ChipVariant = 'solid' | 'outlined' | 'ghost';
type ChipSize = 'sm' | 'md' | 'lg';

interface ChipProps extends Omit<RNEChipProps, 'type'> {
  variant?: ChipVariant;
  size?: ChipSize;
  label: string;
  onPress?: () => void;
  icon?: {
    name: string;
    type: string;
  };
  selected?: boolean;
  disabled?: boolean;
}

export const Chip: RneFunctionComponent<ChipProps> = ({
  variant = 'solid',
  size = 'md',
  label,
  onPress,
  icon,
  selected = false,
  disabled = false,
  ...props
}) => {
  const { theme } = useTheme();
  const styles = useStyles();

  const getVariantStyles = () => {
    const variants = {
      solid: {
        containerStyle: [styles.solidChip, selected && styles.selectedSolidChip],
        titleStyle: styles.solidTitle,
      },
      outlined: {
        containerStyle: [styles.outlinedChip, selected && styles.selectedOutlinedChip],
        titleStyle: [styles.outlinedTitle, selected && styles.selectedOutlinedTitle],
      },
      ghost: {
        containerStyle: [styles.ghostChip, selected && styles.selectedGhostChip],
        titleStyle: [styles.ghostTitle, selected && styles.selectedGhostTitle],
      },
    };
    return variants[variant];
  };

  const getSizeStyles = () => {
    const sizes = {
      sm: styles.smallChip,
      md: styles.mediumChip,
      lg: styles.largeChip,
    };
    return sizes[size];
  };

  const renderIcon = () => {
    if (!icon) return undefined;
    return {
      name: icon.name,
      type: icon.type,
      size: size === 'sm' ? 16 : size === 'md' ? 18 : 20,
      color: variant === 'solid' ? theme.colors.white : theme.colors.primary,
    };
  };

  return (
    <Pressable onPress={disabled ? undefined : onPress}>
      <RNEChip
        title={label}
        type={variant === 'outlined' ? 'outline' : 'solid'}
        containerStyle={[
          styles.baseChip,
          getVariantStyles().containerStyle,
          getSizeStyles(),
          disabled && styles.disabledChip,
        ]}
        titleStyle={[
          styles.baseTitle,
          getVariantStyles().titleStyle,
          disabled && styles.disabledTitle,
        ]}
        icon={renderIcon()}
        {...props}
      />
    </Pressable>
  );
};

const useStyles = makeStyles((theme) => ({
  baseChip: {
    borderRadius: 16,
  },
  baseTitle: {
    fontSize: 14,
    fontWeight: '500',
  },
  // Variant Styles
  solidChip: {
    backgroundColor: theme.colors.primary,
  },
  selectedSolidChip: {
    backgroundColor: theme.colors.secondary,
  },
  solidTitle: {
    color: theme.colors.white,
  },
  outlinedChip: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: theme.colors.primary,
  },
  selectedOutlinedChip: {
    borderColor: theme.colors.secondary,
  },
  outlinedTitle: {
    color: theme.colors.primary,
  },
  selectedOutlinedTitle: {
    color: theme.colors.secondary,
  },
  ghostChip: {
    backgroundColor: `${theme.colors.primary}20`,
  },
  selectedGhostChip: {
    backgroundColor: `${theme.colors.secondary}20`,
  },
  ghostTitle: {
    color: theme.colors.primary,
  },
  selectedGhostTitle: {
    color: theme.colors.secondary,
  },
  // Size Styles
  smallChip: {
    height: 24,
    paddingHorizontal: 8,
  },
  mediumChip: {
    height: 32,
    paddingHorizontal: 12,
  },
  largeChip: {
    height: 40,
    paddingHorizontal: 16,
  },
  // State Styles
  disabledChip: {
    opacity: 0.5,
  },
  disabledTitle: {
    color: theme.colors.grey3,
  },
}));

export default Chip;
