import React from 'react';

import { Text } from '@rneui/themed';
import { View } from 'react-native';

import { useAuth } from '../../contexts/AuthContext';

export default function Analytics() {
  const { user } = useAuth();

  return (
    <View>
      <Text h4>Analytics</Text>
      <Text>Coming soon: Detailed analytics and insights about your productivity patterns</Text>
    </View>
  );
}
