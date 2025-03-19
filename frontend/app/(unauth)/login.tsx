import { useState } from 'react';

import { Input, Button, Text } from '@rneui/themed';
import { Link } from 'expo-router';
import { Platform, StyleSheet, View } from 'react-native';

import { useAuth } from '@/contexts/AuthContext';


export default function LoginScreen() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleLogin = async () => {
    try {
      setLoading(true);
      await login(email, password);
    } catch (error: any) {
      console.error('Login error:', error);
      // Handle error appropriately
    } finally {
      setLoading(false);
    }
  };

  // Use native form elements on web platform
  if (Platform.OS === 'web') {
    return (
      <View style={styles.container}>
        <Text h3 style={styles.title}>Welcome Back!</Text>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleLogin();
          }}
        >
          <div style={styles.inputContainer}>
            <label htmlFor="email" style={styles.label}>Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Email"
              required
              style={styles.webInput}
            />
          </div>
          <div style={styles.inputContainer}>
            <label htmlFor="password" style={styles.label}>Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
              required
              style={styles.webInput}
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="login-button"
            style={{
              width: '100%',
              padding: '12px',
              backgroundColor: '#2089dc',
              color: '#fff',
              borderRadius: '5px',
              fontSize: '16px',
              cursor: 'pointer',
              marginTop: '20px',
              border: 0,
            }}
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
        <View style={styles.footer}>
          <Text>Don't have an account? </Text>
          <Link href="/register" style={styles.link}>
            <Text style={styles.linkText}>Sign up</Text>
          </Link>
        </View>
      </View>
    );
  }

  // Use React Native elements on native platforms
  return (
    <View style={styles.container}>
      <Text h3 style={styles.title}>Welcome Back!</Text>
      <View style={styles.form}>
        <Input
          placeholder="Email"
          value={email}
          onChangeText={setEmail}
          autoCapitalize="none"
          keyboardType="email-address"
          style={styles.input}
        />
        <Input
          placeholder="Password"
          value={password}
          onChangeText={setPassword}
          secureTextEntry
          style={styles.input}
        />
        <Button
          title="Sign In"
          onPress={handleLogin}
          loading={loading}
          buttonStyle={styles.button}
        />
      </View>
      <View style={styles.footer}>
        <Text>Don't have an account? </Text>
        <Link href="/register" style={styles.link}>
          <Text style={styles.linkText}>Sign up</Text>
        </Link>
      </View>
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
    textAlign: 'center',
    marginBottom: 30,
  },
  form: {
    width: '100%',
    maxWidth: 400,
    alignSelf: 'center',
  },
  input: {
    marginBottom: 10,
  },
  inputContainer: {
    marginBottom: 15,
  },
  label: {
    marginBottom: 5,
    fontWeight: '500',
  },
  webInput: {
    width: '100%',
    padding: 10,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 5,
    fontSize: 16,
  },
  button: {
    marginTop: 20,
    backgroundColor: '#2089dc',
    borderRadius: 5,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: 20,
  },
  link: {
    marginLeft: 5,
  },
  linkText: {
    color: '#2089dc',
  },
});
