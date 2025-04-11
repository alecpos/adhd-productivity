import React, { useState } from 'react';

import DateTimePicker from '@react-native-community/datetimepicker';
import { Text, Icon, makeStyles } from '@rneui/themed';
import { format } from 'date-fns';
import { View, Platform, TouchableOpacity } from 'react-native';

interface CustomDateTimePickerProps {
  value: Date;
  onChange: (date: Date) => void;
  mode?: 'date' | 'time' | 'datetime';
  label?: string;
  error?: string;
  minimumDate?: Date;
  maximumDate?: Date;
}

export const CustomDateTimePicker: React.FC<CustomDateTimePickerProps> = ({
  value,
  onChange,
  mode = 'date',
  label,
  error,
  minimumDate,
  maximumDate,
}) => {
  const [show, setShow] = useState(false);
  const styles = useStyles();

  const handleChange = (event: any, selectedDate?: Date) => {
    setShow(Platform.OS === 'ios');
    if (selectedDate) {
      onChange(selectedDate);
    }
  };

  const formatDisplayValue = () => {
    switch (mode) {
      case 'time':
        return format(value, 'HH:mm');
      case 'datetime':
        return format(value, 'dd MMM yyyy HH:mm');
      default:
        return format(value, 'dd MMM yyyy');
    }
  };

  return (
    <View style={styles.container}>
      {label && <Text style={styles.label}>{label}</Text>}

      <TouchableOpacity
        style={[styles.input, ...(error ? [styles.errorInput] : [])]}
        onPress={() => setShow(true)}
      >
        <Text style={styles.value}>{formatDisplayValue()}</Text>
        <Icon
          name={mode === 'time' ? 'access-time' : 'calendar-today'}
          type="material"
          size={20}
          color={styles.icon.color}
        />
      </TouchableOpacity>

      {error && <Text style={styles.errorText}>{error}</Text>}

      {show && (
        <DateTimePicker
          value={value}
          mode={mode}
          display="default"
          onChange={handleChange}
          minimumDate={minimumDate}
          maximumDate={maximumDate}
        />
      )}
    </View>
  );
};

const useStyles = makeStyles((theme) => ({
  container: {
    marginBottom: theme.spacing.md,
  },
  label: {
    marginBottom: theme.spacing.xs,
    fontSize: theme.fontSize.sm,
    color: theme.colors.grey1,
  },
  input: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    height: 48,
    paddingHorizontal: theme.spacing.md,
    borderWidth: 1,
    borderColor: theme.colors.grey4,
    borderRadius: theme.borderRadius.md,
    backgroundColor: theme.colors.white,
  },
  errorInput: {
    borderColor: theme.colors.error,
  },
  value: {
    fontSize: theme.fontSize.md,
    color: theme.colors.grey1,
  },
  icon: {
    color: theme.colors.grey2,
  },
  errorText: {
    marginTop: theme.spacing.xs,
    fontSize: theme.fontSize.xs,
    color: theme.colors.error,
  },
}));
