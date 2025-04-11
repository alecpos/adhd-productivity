import React, { useState, useEffect } from 'react';

import { Text, Button } from '@rneui/themed';
import { View } from 'react-native';

export default function FocusTimer() {
  const [isRunning, setIsRunning] = useState(false);
  const [time, setTime] = useState(0);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isRunning) {
      interval = setInterval(() => {
        setTime((prevTime) => prevTime + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isRunning]);

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = seconds % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes
      .toString()
      .padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const handleStartStop = () => {
    setIsRunning(!isRunning);
  };

  const handleReset = () => {
    setIsRunning(false);
    setTime(0);
  };

  return (
    <View>
      <Text h4>Focus Timer</Text>
      <Text h3>{formatTime(time)}</Text>
      <View style={{ flexDirection: 'row', justifyContent: 'center', gap: 10 }}>
        <Button
          title={isRunning ? 'Stop' : 'Start'}
          onPress={handleStartStop}
        />
        <Button
          title="Reset"
          onPress={handleReset}
        />
      </View>
    </View>
  );
}
