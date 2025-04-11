import React from 'react';

import { Text } from '@rneui/themed';
import { View } from 'react-native';

import { mentalHealthService } from '@/app/services/mental-health';

import { useAuth } from '../../contexts/AuthContext';

import MentalHealthInsights from './Mental/MentalHealthInsights';
import MentalHealthLogForm from './Mental/MentalHealthLogForm';



export default function MentalHealthTracker() {
  const { user } = useAuth();

  const handleSubmit = async (data: any) => {
    try {
      await mentalHealthService.createLog({
        ...data,
        userId: user?.id,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error submitting mental health log:', error);
    }
  };

  return (
    <View>
      <Text h4>Mental Health Tracking</Text>
      <MentalHealthLogForm
        onSubmit={handleSubmit}
        quickMode={true}
        onSuccess={() => {}}
      />
      <MentalHealthInsights userId={user?.id || ''} />
    </View>
  );
}
