import React from 'react';

import { Picker } from '@react-native-picker/picker';
import { Input, Text } from '@rneui/themed';
import { useTheme } from '@rneui/themed';
import { View, StyleSheet } from 'react-native';

interface SelectOption {
  label: string;
  value: string | number;
}

interface SelectProps {
  value: string | number;
  onValueChange: (value: string | number) => void;
  options: SelectOption[];
  label?: string;
  placeholder?: string;
  error?: string;
  disabled?: boolean;
}

export const Select: React.FC<SelectProps> = ({
  value,
  onValueChange,
  options,
  label,
  placeholder,
  error,
  disabled = false,
}) => {
  const { theme } = useTheme();

  const styles = StyleSheet.create({
    container: {
      marginBottom: 16,
    },
    label: {
      fontSize: 16,
      fontWeight: '600',
      marginBottom: 8,
      color: theme.colors.grey3,
    },
    pickerContainer: {
      borderWidth: 1,
      borderColor: error ? theme.colors.error : theme.colors.grey3,
      borderRadius: 8,
      backgroundColor: disabled ? theme.colors.grey5 : theme.colors.background,
    },
    picker: {
      height: 50,
      color: theme.colors.black,
    },
    error: {
      color: theme.colors.error,
      fontSize: 12,
      marginTop: 4,
    },
  });

  return (
    <View style={styles.container}>
      {label && <Text style={styles.label}>{label}</Text>}
      <View style={styles.pickerContainer}>
        <Picker
          selectedValue={value}
          onValueChange={onValueChange}
          enabled={!disabled}
          style={styles.picker}
        >
          {placeholder && (
            <Picker.Item label={placeholder} value="" enabled={false} />
          )}
          {options.map((option) => (
            <Picker.Item
              key={option.value}
              label={option.label}
              value={option.value}
            />
          ))}
        </Picker>
      </View>
      {error && <Text style={styles.error}>{error}</Text>}
    </View>
  );
};

export default Select; 