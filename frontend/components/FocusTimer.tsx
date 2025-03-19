import React, { useState, useEffect, useCallback } from 'react';

import { Ionicons } from '@expo/vector-icons';
import { Text, Card, useTheme, Button, Slider } from '@rneui/themed';
import { View, StyleSheet, Animated } from 'react-native';

import { AnimatedButton } from './ui/AnimatedButton';

interface TimerState {
  minutes: number;
  seconds: number;
  isRunning: boolean;
  isPaused: boolean;
  isBreak: boolean;
  cyclesCompleted: number;
}

interface TimerSettings {
  workDuration: number;
  shortBreakDuration: number;
  longBreakDuration: number;
  cyclesBeforeLongBreak: number;
}

export function FocusTimer() {
  const { theme } = useTheme();
  const [settings, setSettings] = useState<TimerSettings>({
    workDuration: 25,
    shortBreakDuration: 5,
    longBreakDuration: 15,
    cyclesBeforeLongBreak: 4
  });
  
  const [timer, setTimer] = useState<TimerState>({
    minutes: settings.workDuration,
    seconds: 0,
    isRunning: false,
    isPaused: false,
    isBreak: false,
    cyclesCompleted: 0
  });

  const [showSettings, setShowSettings] = useState(false);
  const [progressAnim] = useState(new Animated.Value(0));

  const formatTime = (minutes: number, seconds: number) => {
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  };

  const resetTimer = useCallback(() => {
    setTimer({
      minutes: settings.workDuration,
      seconds: 0,
      isRunning: false,
      isPaused: false,
      isBreak: false,
      cyclesCompleted: 0
    });
    progressAnim.setValue(0);
  }, [settings.workDuration]);

  const toggleTimer = useCallback(() => {
    if (!timer.isRunning) {
      setTimer(prev => ({ ...prev, isRunning: true, isPaused: false }));
      // Start progress animation
      Animated.timing(progressAnim, {
        toValue: 1,
        duration: (timer.minutes * 60 + timer.seconds) * 1000,
        useNativeDriver: false
      }).start();
    } else {
      setTimer(prev => ({ ...prev, isPaused: !prev.isPaused }));
      if (!timer.isPaused) {
        // Pause animation
        progressAnim.stopAnimation();
      } else {
        // Resume animation
        Animated.timing(progressAnim, {
          toValue: 1,
          duration: (timer.minutes * 60 + timer.seconds) * 1000,
          useNativeDriver: false
        }).start();
      }
    }
  }, [timer.isRunning, timer.isPaused, timer.minutes, timer.seconds]);

  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (timer.isRunning && !timer.isPaused) {
      interval = setInterval(() => {
        setTimer(prev => {
          if (prev.minutes === 0 && prev.seconds === 0) {
            clearInterval(interval);
            // Handle cycle completion
            const nextCycles = prev.isBreak ? prev.cyclesCompleted + 1 : prev.cyclesCompleted;
            const isLongBreakDue = nextCycles % settings.cyclesBeforeLongBreak === 0;
            const nextBreakDuration = isLongBreakDue ? settings.longBreakDuration : settings.shortBreakDuration;
            
            return {
              ...prev,
              minutes: prev.isBreak ? settings.workDuration : nextBreakDuration,
              seconds: 0,
              isBreak: !prev.isBreak,
              cyclesCompleted: nextCycles
            };
          }

          if (prev.seconds === 0) {
            return {
              ...prev,
              minutes: prev.minutes - 1,
              seconds: 59,
            };
          }

          return {
            ...prev,
            seconds: prev.seconds - 1,
          };
        });
      }, 1000);
    }

    return () => clearInterval(interval);
  }, [timer.isRunning, timer.isPaused, settings]);

  const renderSettings = () => (
    <View style={styles.settingsContainer}>
      <Text style={styles.settingLabel}>Work Duration (minutes)</Text>
      <Slider
        value={settings.workDuration}
        onValueChange={(value) => setSettings(prev => ({ ...prev, workDuration: value }))}
        minimumValue={1}
        maximumValue={60}
        step={1}
        thumbStyle={styles.sliderThumb}
      />
      
      <Text style={styles.settingLabel}>Short Break Duration (minutes)</Text>
      <Slider
        value={settings.shortBreakDuration}
        onValueChange={(value) => setSettings(prev => ({ ...prev, shortBreakDuration: value }))}
        minimumValue={1}
        maximumValue={30}
        step={1}
        thumbStyle={styles.sliderThumb}
      />
      
      <Text style={styles.settingLabel}>Long Break Duration (minutes)</Text>
      <Slider
        value={settings.longBreakDuration}
        onValueChange={(value) => setSettings(prev => ({ ...prev, longBreakDuration: value }))}
        minimumValue={5}
        maximumValue={45}
        step={1}
        thumbStyle={styles.sliderThumb}
      />
      
      <Text style={styles.settingLabel}>Cycles Before Long Break</Text>
      <Slider
        value={settings.cyclesBeforeLongBreak}
        onValueChange={(value) => setSettings(prev => ({ ...prev, cyclesBeforeLongBreak: value }))}
        minimumValue={2}
        maximumValue={6}
        step={1}
        thumbStyle={styles.sliderThumb}
      />
    </View>
  );

  return (
    <Card containerStyle={styles.container}>
      <View style={styles.header}>
        <Card.Title>{timer.isBreak ? 'Break Time' : 'Focus Time'}</Card.Title>
        <Button
          type="clear"
          icon={<Ionicons name="settings-outline" size={24} color={theme.colors.primary} />}
          onPress={() => setShowSettings(!showSettings)}
        />
      </View>
      
      {showSettings ? (
        renderSettings()
      ) : (
        <>
          <View style={styles.timerContainer}>
            <Animated.View style={[
              styles.progressBar,
              {
                width: progressAnim.interpolate({
                  inputRange: [0, 1],
                  outputRange: ['0%', '100%']
                })
              }
            ]} />
            
            <Text style={[styles.timer, { color: theme.colors.primary }]}>
              {formatTime(timer.minutes, timer.seconds)}
            </Text>
            
            <Text style={styles.cycleInfo}>
              Cycle: {Math.floor(timer.cyclesCompleted / 2) + 1} / {settings.cyclesBeforeLongBreak}
            </Text>
            
            <View style={styles.controls}>
              <AnimatedButton
                icon={
                  <Ionicons
                    name={timer.isRunning && !timer.isPaused ? 'pause' : 'play'}
                    size={24}
                    color="white"
                  />
                }
                onPress={toggleTimer}
                scaleOnPress
                containerStyle={[styles.button, styles.controlButton]}
              />
              
              <AnimatedButton
                icon={
                  <Ionicons
                    name="refresh"
                    size={24}
                    color="white"
                  />
                }
                onPress={resetTimer}
                scaleOnPress
                containerStyle={[styles.button, styles.controlButton]}
                disabled={!timer.isRunning}
              />
            </View>
          </View>

          <View style={styles.infoContainer}>
            <Text style={styles.infoText}>
              {timer.isBreak 
                ? '🧘‍♂️ Take a break and recharge'
                : '🎯 Stay focused on your task'}
            </Text>
            <Text style={styles.infoText}>
              {timer.isBreak
                ? `Next work session: ${settings.workDuration} minutes`
                : `Next break: ${timer.cyclesCompleted % settings.cyclesBeforeLongBreak === settings.cyclesBeforeLongBreak - 1 
                    ? settings.longBreakDuration 
                    : settings.shortBreakDuration} minutes`}
            </Text>
          </View>
        </>
      )}
    </Card>
  );
}

const styles = StyleSheet.create({
  container: {
    borderRadius: 10,
    padding: 15,
    marginBottom: 15,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  timerContainer: {
    alignItems: 'center',
    marginVertical: 20,
    position: 'relative',
  },
  progressBar: {
    position: 'absolute',
    top: 0,
    left: 0,
    height: 3,
    backgroundColor: '#4CAF50',
  },
  timer: {
    fontSize: 48,
    fontWeight: 'bold',
    fontVariant: ['tabular-nums'],
  },
  cycleInfo: {
    fontSize: 16,
    color: '#666',
    marginTop: 10,
  },
  controls: {
    flexDirection: 'row',
    gap: 20,
    marginTop: 20,
  },
  button: {
    borderRadius: 8,
    overflow: 'hidden',
  },
  controlButton: {
    width: 60,
  },
  infoContainer: {
    marginTop: 20,
    padding: 15,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
  },
  infoText: {
    fontSize: 14,
    marginBottom: 8,
    color: '#495057',
  },
  settingsContainer: {
    padding: 15,
  },
  settingLabel: {
    fontSize: 14,
    fontWeight: '500',
    marginTop: 15,
    marginBottom: 5,
  },
  sliderThumb: {
    backgroundColor: '#4CAF50',
    width: 20,
    height: 20,
  },
}); 