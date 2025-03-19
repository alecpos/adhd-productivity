import React from 'react';

import { Text, makeStyles, useTheme } from '@rneui/themed';
import { View, Modal, TouchableOpacity, ScrollView } from 'react-native';

interface ActionSheetOption {
  label: string;
  onPress: () => void;
  icon?: string;
  destructive?: boolean;
}

interface ActionSheetProps {
  visible: boolean;
  onClose: () => void;
  options: ActionSheetOption[];
  title?: string;
}

export const ActionSheet: React.FC<ActionSheetProps> = ({
  visible,
  onClose,
  options,
  title,
}) => {
  const styles = useStyles();
  const { theme } = useTheme();

  return (
    <Modal
      visible={visible}
      transparent
      animationType="slide"
      onRequestClose={onClose}
    >
      <TouchableOpacity 
        style={styles.overlay} 
        activeOpacity={1} 
        onPress={onClose}
      >
        <View style={styles.content}>
          {title && <Text style={styles.title}>{title}</Text>}
          <ScrollView>
            {options.map((option, index) => (
              <TouchableOpacity
                key={index}
                style={styles.option}
                onPress={() => {
                  option.onPress();
                  onClose();
                }}
              >
                <Text style={[
                  styles.optionText,
                  option.destructive && styles.destructiveText
                ]}>
                  {option.label}
                </Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>
      </TouchableOpacity>
    </Modal>
  );
};

const useStyles = makeStyles((theme) => ({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.4)',
    justifyContent: 'flex-end',
  },
  content: {
    backgroundColor: theme.colors.background,
    borderTopLeftRadius: theme.borderRadius.lg,
    borderTopRightRadius: theme.borderRadius.lg,
    paddingBottom: theme.spacing.xl,
    maxHeight: '70%',
  },
  title: {
    textAlign: 'center',
    padding: theme.spacing.md,
    fontSize: theme.fontSize.lg,
    fontWeight: 'bold',
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.grey5,
  },
  option: {
    padding: theme.spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.grey5,
  },
  optionText: {
    fontSize: theme.fontSize.md,
    color: theme.colors.text,
  },
  destructiveText: {
    color: theme.colors.error,
  },
})); 