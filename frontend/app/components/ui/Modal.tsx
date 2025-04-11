// app/components/ui/Modal.tsx
import React from 'react';

import { makeStyles } from '@rneui/themed';
import { Modal as RNModal, View, TouchableOpacity } from 'react-native';


import { Button } from './Button';
import { Card } from './Card';

import type { ViewStyle, GestureResponderEvent } from 'react-native';


export interface ModalProps {
  visible: boolean;
  onClose: () => void;
  children: React.ReactNode;
  title?: string;
  footer?: React.ReactNode;
  width?: number | string;
  height?: number | string;
}

export const Modal: React.FC<ModalProps> = ({
  visible,
  onClose,
  children,
  title,
  footer,
  width = '90%',
  height = 'auto',
}) => {
  const styles = useStyles();

  return (
    <RNModal
      visible={visible}
      transparent
      animationType="fade"
      onRequestClose={onClose}
    >
      <TouchableOpacity
        style={styles.overlay}
        activeOpacity={1}
        onPress={(event: GestureResponderEvent) => {
          event.stopPropagation();
        }}
      >
        <View style={[
          styles.container,
          { width: typeof width === 'number' ? width : width,
            height: typeof height === 'number' ? height : height
          } as ViewStyle
        ]}>
          <Card
            variant="elevated"
          >
            {children}
          </Card>
          {footer && <View style={styles.footer}>{footer}</View>}
        </View>
      </TouchableOpacity>
    </RNModal>
  );
};

const useStyles = makeStyles((theme) => ({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  container: {
    backgroundColor: 'transparent',
    borderRadius: theme.spacing.lg,
    overflow: 'hidden',
  },
  content: {
    padding: theme.spacing.lg,
  },
  footer: {
    padding: theme.spacing.md,
    borderTopWidth: 1,
    borderTopColor: theme.colors.grey5,
  },
}));

export default Modal;
