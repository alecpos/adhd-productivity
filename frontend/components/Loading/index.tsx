import React from 'react';

import { LoadingAnimation } from './LoadingAnimation';
import { LoadingSpinner } from './LoadingSpinner';

import type { LoadingAnimationProps } from './LoadingAnimation';
import type { LoadingSpinnerProps } from './LoadingSpinner';


export type LoadingVariant = 'spinner' | 'animation';

export interface LoadingProps extends Omit<LoadingSpinnerProps & LoadingAnimationProps, 'source'> {
  variant?: LoadingVariant;
  animationSource?: LoadingAnimationProps['source'];
}

type LoadingComponent = React.FC<LoadingProps> & {
  Spinner: typeof LoadingSpinner;
  Animation: typeof LoadingAnimation;
};

const LoadingBase: React.FC<LoadingProps> = ({
  variant = 'spinner',
  animationSource,
  ...props
}) => {
  if (variant === 'animation') {
    return <LoadingAnimation source={animationSource} {...props} />;
  }
  return <LoadingSpinner {...props} />;
};

export const Loading = LoadingBase as LoadingComponent;
Loading.Spinner = LoadingSpinner;
Loading.Animation = LoadingAnimation;

// Export types
export type { LoadingSpinnerProps } from './LoadingSpinner';
export type { LoadingAnimationProps } from './LoadingAnimation';
