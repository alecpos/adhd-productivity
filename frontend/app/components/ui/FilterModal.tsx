import React, { useState } from 'react';

import { Text, makeStyles } from '@rneui/themed';
import { View, ScrollView } from 'react-native';

import { Button } from './Button';
import { Chip } from './Chip';
import { Modal } from './Modal';

interface FilterOption {
  id: string;
  label: string;
  options: string[];
}

interface FilterModalProps {
  visible: boolean;
  onClose: () => void;
  options: FilterOption[];
  selectedFilters: Record<string, string[]>;
  onApply: (filters: Record<string, string[]>) => void;
}

export const FilterModal: React.FC<FilterModalProps> = ({
  visible,
  onClose,
  options,
  selectedFilters,
  onApply,
}) => {
  const [localFilters, setLocalFilters] = useState(selectedFilters);
  const styles = useStyles();

  const handleToggleOption = (categoryId: string, option: string) => {
    setLocalFilters(prev => {
      const current = prev[categoryId] || [];
      const updated = current.includes(option)
        ? current.filter(item => item !== option)
        : [...current, option];

      return {
        ...prev,
        [categoryId]: updated,
      };
    });
  };

  const handleReset = () => {
    setLocalFilters({});
  };

  const handleApply = () => {
    onApply(localFilters);
    onClose();
  };

  return (
    <Modal
      visible={visible}
      onClose={onClose}
      title="Filters"
      footer={
        <View style={styles.footer}>
          <Button
            variant="ghost"
            onPress={handleReset}
            title="Reset"
          />
          <Button
            onPress={handleApply}
            title="Apply Filters"
          />
        </View>
      }
    >
      <ScrollView style={styles.content}>
        {options.map(category => (
          <View key={category.id} style={styles.category}>
            <Text style={styles.categoryTitle}>{category.label}</Text>
            <View style={styles.options}>
              {category.options.map(option => (
                <Chip
                  key={option}
                  label={option}
                  selected={localFilters[category.id]?.includes(option)}
                  onPress={() => handleToggleOption(category.id, option)}
                  variant="outlined"
                />
              ))}
            </View>
          </View>
        ))}
      </ScrollView>
    </Modal>
  );
};

const useStyles = makeStyles((theme) => ({
  content: {
    maxHeight: '80%',
  },
  category: {
    marginBottom: theme.spacing.lg,
  },
  categoryTitle: {
    fontSize: theme.fontSize.md,
    fontWeight: 'bold',
    marginBottom: theme.spacing.sm,
  },
  options: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: theme.spacing.sm,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    gap: theme.spacing.sm,
  },
}));
