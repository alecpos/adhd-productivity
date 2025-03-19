import React from 'react';

import { makeStyles } from '@rneui/themed';
import { View, ScrollView } from 'react-native';

import { useAuth } from '../../../contexts/AuthContext';
import EnergyLevelTracker from '../../components/EnergyLevelTracker';
import MentalHealthTracker from '../../components/MentalHealthTracker';
import { useToast } from '../../components/ui/ToastProvider';
import { mentalHealthService } from '../../services/mental-health';
import MentalHealthInsights from '../Mental/MentalHealthInsights';
import MentalHealthLogForm from '../Mental/MentalHealthLogForm';

export default function WellnessTab() {
  const { user } = useAuth();
  const { showToast } = useToast();
  const styles = useStyles();

  const handleMoodSubmit = async (data: any) => {
    if (!user?.id) return;

    try {
      await mentalHealthService.createLog({
        ...data,
        userId: user.id,
        timestamp: new Date().toISOString()
      });
      showToast({
        type: 'success',
        message: 'Mood logged successfully',
        duration: 3000
      });
    } catch (error) {
      showToast({
        type: 'error',
        message: 'Failed to log mood',
        duration: 3000
      });
      console.error('Error logging mood:', error);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.section}>
        <MentalHealthTracker />
      </View>

      <View style={styles.section}>
        <EnergyLevelTracker />
      </View>

      <View style={styles.section}>
        <MentalHealthLogForm 
          onSubmit={handleMoodSubmit}
          quickMode={true}
        />
      </View>

      {user?.id && (
        <View style={styles.section}>
          <MentalHealthInsights userId={user.id} />
        </View>
      )}
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