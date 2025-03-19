import React, { useState } from 'react';

import { makeStyles, useTheme } from '@rneui/themed';
import { View, TextInput, StyleSheet, Text } from 'react-native';

import { AnimatedButton } from '../../components/ui/AnimatedButton';
import { useAuth } from '../../contexts/AuthContext';

export default function RegisterScreen() {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const { theme } = useTheme();
  
  const { register, loading, error } = useAuth();

  const handleRegister = async () => {
    if (!email || !username || !password || !fullName) {
      return;
    }
    await register(email, username, password, fullName);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Register</Text>
      
      {error && <Text style={styles.error}>{error}</Text>}
      
      <TextInput
        style={[styles.input, { borderColor: theme.colors.grey3 }]}
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
        autoCapitalize="none"
      />
      
      <TextInput
        style={[styles.input, { borderColor: theme.colors.grey3 }]}
        placeholder="Username"
        value={username}
        onChangeText={setUsername}
        autoCapitalize="none"
      />
      
      <TextInput
        style={[styles.input, { borderColor: theme.colors.grey3 }]}
        placeholder="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />
      
      <TextInput
        style={[styles.input, { borderColor: theme.colors.grey3 }]}
        placeholder="Full Name"
        value={fullName}
        onChangeText={setFullName}
      />
      
      <AnimatedButton
        title={loading ? "Registering..." : "Register"}
        onPress={handleRegister}
        disabled={loading || !email || !username || !password || !fullName}
        loading={loading}
        scaleOnPress
        pulseOnLoad
        buttonStyle={{ backgroundColor: theme.colors.primary }}
        containerStyle={styles.button}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    justifyContent: 'center',
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 24,
    textAlign: 'center',
  },
  input: {
    height: 48,
    borderWidth: 1,
    marginBottom: 16,
    paddingHorizontal: 12,
    borderRadius: 8,
    fontSize: 16,
  },
  error: {
    color: 'red',
    marginBottom: 16,
    textAlign: 'center',
  },
  button: {
    marginTop: 8,
    borderRadius: 8,
    overflow: 'hidden',
  },
}); 