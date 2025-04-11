// app/components/ui/ConfirmationDialog.tsx
import React from 'react';

import { Text } from '@rneui/themed';
import { View } from 'react-native';

import { Button } from './Button';
import { Modal } from './Modal';

interface ConfirmationDialogProps {
  visible: boolean;
  title: string;
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
  confirmText?: string;
  cancelText?: string;
}

export const ConfirmationDialog: React.FC<ConfirmationDialogProps> = ({
  visible,
  title,
  message,
  onConfirm,
  onCancel,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
}) => {
  return (
    <Modal
      visible={visible}
      onClose={onCancel}
      footer={
        <View style={{ flexDirection: 'row', justifyContent: 'flex-end', gap: 8 }}>
          <Button
            variant="outline"
            title={cancelText}
            onPress={onCancel}
          />
          <Button
            title={confirmText}
            onPress={onConfirm}
          />
        </View>
      }
    >
      <View>
        <Text h4>{title}</Text>
        <Text style={{ marginTop: 8 }}>{message}</Text>
      </View>
    </Modal>
  );
};

export default ConfirmationDialog;
