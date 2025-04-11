import React from 'react';

import { Text, Slider } from '@rneui/themed';
import { View } from 'react-native';

import { useAuth } from '../../contexts/AuthContext';

export default function EnergyLevelTracker() {
  const { user } = useAuth();
  const [energyLevel, setEnergyLevel] = React.useState(5);

  return (
    <View>
      <Text h4>Energy Level</Text>
      <Text>Current Level: {energyLevel}</Text>
      <Slider
        value={energyLevel}
        onValueChange={setEnergyLevel}
        minimumValue={1}
        maximumValue={10}
        step={1}
        trackStyle={{ height: 10, backgroundColor: 'transparent' }}
        thumbStyle={{ height: 20, width: 20, backgroundColor: 'transparent' }}
        thumbProps={{
          children: (
            <View
              style={{
                height: 20,
                width: 20,
                backgroundColor: '#2089dc',
                borderRadius: 10,
              }}
            />
          ),
        }}
      />
    </View>
  );
}
