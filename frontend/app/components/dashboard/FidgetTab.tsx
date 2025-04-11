import React, { useState } from 'react';

import { makeStyles } from '@rneui/themed';
import { Button } from '@rneui/themed';
import { View } from 'react-native';


import { FidgetCube } from '../../../components/FidgetCube';
import { FidgetSpinner } from '../../../components/FidgetSpinner';

import type { ViewStyle } from 'react-native';


interface Styles {
  container: ViewStyle;
  toggleContainer: ViewStyle;
}

export default function FidgetTab() {
  const styles = useStyles();
  const [currentFidget, setCurrentFidget] = useState('cube');

  const toggleFidget = () => {
    setCurrentFidget(current => current === 'cube' ? 'spinner' : 'cube');
  };

  return (
    <View style={styles.container}>
      <View style={styles.toggleContainer}>
        <Button
          title={`Switch to ${currentFidget === 'cube' ? 'Spinner' : 'Cube'}`}
          onPress={toggleFidget}
        />
      </View>

      {currentFidget === 'cube' ? (
        <FidgetCube
          size={200}
          primaryColor="#4A90E2"
          secondaryColor="#2E5C8A"
          onInteraction={(type, intensity) => {
            console.log('Cube interaction:', type, intensity);
          }}
        />
      ) : (
        <FidgetSpinner
          size={200}
          primaryColor="#4A90E2"
          secondaryColor="#2E5C8A"
          onSpinComplete={(speed) => {
            console.log('Spin complete:', speed);
          }}
        />
      )}
    </View>
  );
}

const useStyles = makeStyles((theme) => ({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  toggleContainer: {
    position: 'absolute',
    top: 20,
    width: '100%',
    alignItems: 'center',
  },
}));
