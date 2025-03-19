import React from 'react';

import { Card as RNECard, makeStyles, useTheme } from '@rneui/themed';
import { View } from 'react-native';

import type { CardProps as RNECardProps } from '@rneui/themed';
import type { StyleProp, ViewStyle } from 'react-native';

type CardVariant = 'elevated' | 'outlined' | 'filled';
type CardSize = 'small' | 'medium' | 'large';

interface CardProps extends Omit<RNECardProps, 'containerStyle'> {
  variant?: CardVariant;
  size?: CardSize;
  noPadding?: boolean;
  fullWidth?: boolean;
  children: React.ReactNode;
  testID: string;
}

export const Card: React.FC<CardProps> = ({
  variant = 'elevated',
  size = 'medium',
  noPadding = false,
  fullWidth = false,
  children,
  testID,
  ...props
}) => {
  const styles = useStyles();
  const { theme: _theme } = useTheme();

  const getVariantStyle = (): StyleProp<ViewStyle> => {
    switch (variant) {
      case 'elevated':
        return styles.elevatedCard;
      case 'outlined':
        return styles.outlinedCard;
      case 'filled':
        return styles.filledCard;
      default:
        return {};
    }
  };

  const getSizeStyle = (): StyleProp<ViewStyle> => {
    switch (size) {
      case 'small':
        return styles.smallCard;
      case 'medium':
        return styles.mediumCard;
      case 'large':
        return styles.largeCard;
      default:
        return styles.mediumCard;
    }
  };

  return (
    <View testID={testID} style={[fullWidth && styles.fullWidthContainer]}>
      <RNECard
        containerStyle={[
          styles.baseCard,
          getVariantStyle(),
          getSizeStyle(),
          noPadding && styles.noPaddingCard,
          fullWidth && styles.fullWidthCard,
        ]}
        {...props}
      >
        {children}
      </RNECard>
    </View>
  );
};

const useStyles = makeStyles((theme) => ({
  baseCard: {
    borderRadius: 8,
    backgroundColor: theme.colors.background,
    margin: 0,
  },
  elevatedCard: {
    elevation: 3,
    shadowColor: theme.colors.black,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    borderWidth: 0,
  },
  outlinedCard: {
    borderWidth: 1,
    borderColor: theme.colors.grey4,
    elevation: 0,
    shadowColor: 'transparent',
  },
  filledCard: {
    backgroundColor: theme.colors.grey5,
    borderWidth: 0,
    elevation: 0,
    shadowColor: 'transparent',
  },
  smallCard: {
    padding: 8,
  },
  mediumCard: {
    padding: 16,
  },
  largeCard: {
    padding: 24,
  },
  fullWidthContainer: {
    width: '100%',
  },
  fullWidthCard: {
    width: '100%',
    alignSelf: 'stretch',
  },
  noPaddingCard: {
    padding: 0,
  },
})); 