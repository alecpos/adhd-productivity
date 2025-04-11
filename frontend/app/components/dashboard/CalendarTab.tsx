import React from 'react';

import { makeStyles } from '@rneui/themed';
import { View, ScrollView } from 'react-native';

import { BlockScheduler } from '../BlockScheduler';
import { Calendar } from '../Calendar';
import CalendarManager from '../CalendarManager';

export default function CalendarTab() {
  const styles = useStyles();

  return (
    <ScrollView style={styles.container}>
      <View style={styles.section}>
        <Calendar />
      </View>

      <View style={styles.section}>
        <CalendarManager />
      </View>

      <View style={styles.section}>
        <BlockScheduler />
      </View>
    </ScrollView>
  );
}

const useStyles = makeStyles((theme) => ({
  container: {
    flex: 1,
  },
  section: {
    marginVertical: theme.spacing.sm,
    padding: theme.spacing.md,
    backgroundColor: theme.colors.surface,
    borderRadius: theme.spacing.sm,
    shadowColor: theme.colors.grey5,
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
}));
