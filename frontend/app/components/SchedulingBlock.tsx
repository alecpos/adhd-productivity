import React from 'react';

import { Text, useTheme } from '@rneui/themed';
import { format } from 'date-fns';
import { View, StyleSheet } from 'react-native';

interface SchedulingBlockProps {
  startTime: Date;
  endTime: Date;
  type: 'focus' | 'break' | 'long-break';
}

const SchedulingBlock: React.FC<SchedulingBlockProps> = ({ startTime, endTime, type }) => {
  const { theme } = useTheme();

  const getBlockStyle = () => {
    switch (type) {
      case 'focus':
        return {
          backgroundColor: theme.colors.primary + '20', // 20% opacity
          borderColor: theme.colors.primary,
        };
      case 'break':
        return {
          backgroundColor: theme.colors.success + '20',
          borderColor: theme.colors.success,
        };
      case 'long-break':
        return {
          backgroundColor: theme.colors.secondary + '20',
          borderColor: theme.colors.secondary,
        };
    }
  };

  return (
    <View style={[styles.block, getBlockStyle()]}>
      <Text h4>
        {type.charAt(0).toUpperCase() + type.slice(1)} Block
      </Text>
      <Text style={{ color: theme.colors.grey2 }}>
        {format(startTime, 'h:mm a')} - {format(endTime, 'h:mm a')}
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  block: {
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
    borderWidth: 1,
  },
});

export default SchedulingBlock; 