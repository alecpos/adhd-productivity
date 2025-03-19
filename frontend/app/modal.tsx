import { makeStyles } from '@rneui/themed';
import { Text } from '@rneui/themed';
import { StatusBar } from 'expo-status-bar';
import { Platform } from 'react-native';
import {  View } from 'react-native';

import EditScreenInfo from '@/components/EditScreenInfo';


export default function ModalScreen() {
  const styles = useStyles();

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Modal</Text>
      <View style={styles.separator} />
      <EditScreenInfo path="app/modal.tsx" />

      {/* Use a light status bar on iOS to account for the black space above the modal */}
      <StatusBar style={Platform.OS === 'ios' ? 'light' : 'auto'} />
    </View>
  );
}

const useStyles = makeStyles((theme) => ({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  title: {
    fontSize: theme.fontSize.lg,
    fontWeight: 'bold',
  },
  separator: {
    marginVertical: theme.spacing.xl,
    height: 1,
    width: '80%',
    backgroundColor: theme.colors.grey5,
  },
}));
