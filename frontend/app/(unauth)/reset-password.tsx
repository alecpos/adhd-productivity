import React, { useState } from 'react';

import { Input, Button, Text } from '@rneui/themed';
import axios from 'axios';
import { View, StyleSheet, Alert } from 'react-native';

import type { NativeStackScreenProps } from '@react-navigation/native-stack';

type RootStackParamList = {
  Login: undefined;
  Register: undefined;
  ResetPassword: undefined;
};

type Props = NativeStackScreenProps<RootStackParamList, 'ResetPassword'>;

export default function ResetPasswordScreen({ navigation }: Props) {
  const [email, setEmail] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handlePasswordReset = async () => {
    if (newPassword.length < 8) {
      Alert.alert('Validation Error', 'Password must be at least 8 characters long.');
      return;
    }
    setLoading(true);
    try {
      await axios.post('http://127.0.0.1:8000/reset-password', {
        email,
        new_password: newPassword,
      });
      Alert.alert('Password Reset Successful', 'You can now log in with your new password.');
      navigation.navigate('Login');
    } catch (error: any) {
      Alert.alert('Password Reset Failed', error.response?.data?.detail || 'An error occurred.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text h3 style={styles.title}>Reset Password</Text>
      <Input
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        autoCapitalize="none"
        keyboardType="email-address"
        textContentType="emailAddress"
        leftIcon={{ type: 'material', name: 'email' }}
      />
      <Input
        placeholder="New Password"
        value={newPassword}
        onChangeText={setNewPassword}
        secureTextEntry
        textContentType="newPassword"
        leftIcon={{ type: 'material', name: 'lock' }}
      />
      <Button
        title={loading ? 'Resetting...' : 'Reset Password'}
        onPress={handlePasswordReset}
        disabled={loading}
        containerStyle={styles.buttonContainer}
      />
      <Button
        title="Back to Login"
        type="clear"
        onPress={() => navigation.navigate('Login')}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 20,
  },
  title: {
    textAlign: 'center',
    marginBottom: 20,
  },
  buttonContainer: {
    marginVertical: 10,
  },
});
