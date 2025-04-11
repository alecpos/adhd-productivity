import React from 'react';

import { Avatar as RNEAvatar, makeStyles, useTheme } from '@rneui/themed';

import type { AvatarProps as RNEAvatarProps} from '@rneui/themed';

type AvatarSize = 'small' | 'medium' | 'large' | number;
type AvatarVariant = 'circular' | 'rounded' | 'square';

interface AvatarProps extends Omit<RNEAvatarProps, 'size'> {
  size?: AvatarSize;
  variant?: AvatarVariant;
  showBadge?: boolean;
  badgeStatus?: 'success' | 'error' | 'warning';
  onPress?: () => void;
}

export const Avatar: React.FC<AvatarProps> = ({
  size = 'medium',
  variant = 'circular',
  showBadge = false,
  badgeStatus = 'success',
  onPress,
  ...props
}) => {
  const { theme } = useTheme();
  const styles = useStyles();

  const getSize = (): number => {
    if (typeof size === 'number') return size;
    const sizes = {
      small: 32,
      medium: 48,
      large: 64,
    };
    return sizes[size];
  };

  const getBorderRadius = (): number => {
    const avatarSize = getSize();
    const variants = {
      circular: avatarSize / 2,
      rounded: 8,
      square: 0,
    };
    return variants[variant];
  };

  return (
    <RNEAvatar
      size={getSize()}
      containerStyle={[
        styles.container,
        { borderRadius: getBorderRadius() },
      ]}
      onPress={onPress}
      {...(showBadge && {
        badge: {
          status: badgeStatus,
          containerStyle: styles.badgeContainer,
        },
      })}
      {...props}
    />
  );
};

const useStyles = makeStyles((theme) => ({
  container: {
    backgroundColor: theme.colors.grey5,
  },
  badgeContainer: {
    position: 'absolute',
    bottom: 0,
    right: 0,
  },
}));

export default Avatar;
