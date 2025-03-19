import React, { useState } from 'react';

import axios from 'axios';
import { View, TextInput, Button, Alert } from 'react-native';

export default function RegisterScreen({ navigation }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [username, setUsername] = useState('');

  const handleRegister = async () => {
    try {
      await axios.post('http://localhost:8000/register', {
        email,
        password,
        name,
        username,
      });
      Alert.alert('Registration successful', 'You can now log in.');
      navigation.navigate('Login');
    } catch (error) {
      Alert.alert('Registration failed', error.response.data.detail);
    }
  };

  return (
    <View>
      <TextInput
        placeholder="Name"
        value={name}
        onChangeText={setName}
        textContentType="name"
      />
      <TextInput
        placeholder="Username"
        value={username}
        onChangeText={setUsername}
        autoCapitalize="none"
        textContentType="username"
      />
      <TextInput
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        autoCapitalize="none"
        keyboardType="email-address"
        textContentType="emailAddress"
      />
      <TextInput
        placeholder="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
        textContentType="password"
      />
      <Button title="Register" onPress={handleRegister} />
    </View>
  );
}
