import React, { useState } from 'react';

import { Input, Button, Text } from '@rneui/themed';
import axios from 'axios';
import { useRouter } from 'expo-router';
import { View, StyleSheet, Alert } from 'react-native';

export default function RegisterScreen() {
  const [name, setName] = useState('');
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleRegister = async () => {
    if (!name || !username || !email || !password) {
      Alert.alert('Validation Error', 'Please fill in all fields.');
      return;
    }

    setLoading(true);
    try {
      await axios.post('http://localhost:8000/api/auth/register', {
        name,
        username,
        email,
        password,
      });
      Alert.alert('Registration Successful', 'You can now log in.');
      router.replace('/(unauth)/login');
    } catch (error: any) {
      const message = error.response?.data?.detail || 'An error occurred.';
      Alert.alert('Registration Failed', message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text h3>Register</Text>
      <Input
        placeholder="Name"
        value={name}
        onChangeText={setName}
        leftIcon={{ type: 'material', name: 'person' }}
        testID="name-input"
      />
      <Input
        placeholder="Username"
        value={username}
        onChangeText={setUsername}
        autoCapitalize="none"
        leftIcon={{ type: 'material', name: 'account-circle' }}
        testID="username-input"
      />
      <Input
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        autoCapitalize="none"
        keyboardType="email-address"
        textContentType="emailAddress"
        leftIcon={{ type: 'material', name: 'email' }}
        testID="email-input"
      />
      <Input
        placeholder="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
        textContentType="newPassword"
        leftIcon={{ type: 'material', name: 'lock' }}
        returnKeyType="done"
        onSubmitEditing={handleRegister}
        testID="password-input"
      />
      <Button
        title={loading ? 'Registering...' : 'Register'}
        onPress={handleRegister}
        disabled={loading}
        testID="register-button"
      />
      <Button
        title="Back to Login"
        type="clear"
        onPress={() => router.push('/(unauth)/login')}
        testID="back-to-login-button"
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
});
