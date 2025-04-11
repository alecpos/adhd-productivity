import React, { useEffect } from 'react';

import { Text, Button, Card, makeStyles } from '@rneui/themed';
import { useRouter } from 'expo-router';
import { View, ScrollView } from 'react-native';

import { useAuth } from '../../../contexts/AuthContext';
import { useMedical } from '../../../contexts/MedicalContext';

export default function HealthDataScreen() {
  const router = useRouter();
  const { user } = useAuth();
  const styles = useStyles();
  const {
    isAuthenticated,
    healthData,
    loading,
    error,
    authenticate,
    storeHealthData,
    exportData,
    deleteData,
  } = useMedical();

  useEffect(() => {
    if (!isAuthenticated) {
      authenticate();
    }
  }, [isAuthenticated]);

  const handleAddData = async () => {
    if (!user?.id) return;

    // Example of adding new health data
    const newData = {
      id: Date.now().toString(),
      patientId: user.id,
      data: {
        bloodPressure: '120/80',
        heartRate: '72',
        temperature: '98.6',
        notes: 'Regular checkup',
      },
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    await storeHealthData(newData);
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>{error}</Text>
        <Button title="Retry Authentication" onPress={authenticate} />
      </View>
    );
  }

  if (!isAuthenticated) {
    return (
      <View style={styles.container}>
        <Text style={styles.messageText}>Please authenticate to view health data</Text>
        <Button title="Authenticate" onPress={authenticate} />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <Text h3 style={styles.title}>Health Data</Text>

      {healthData ? (
        <Card containerStyle={styles.card}>
          <Card.Title>Latest Health Records</Card.Title>
          <Card.Divider />
          <View>
            <Text style={styles.dataText}>Blood Pressure: {healthData.data.bloodPressure}</Text>
            <Text style={styles.dataText}>Heart Rate: {healthData.data.heartRate}</Text>
            <Text style={styles.dataText}>Temperature: {healthData.data.temperature}</Text>
            <Text style={styles.dataText}>Notes: {healthData.data.notes}</Text>
            <Text style={styles.timestamp}>
              Last Updated: {new Date(healthData.updatedAt).toLocaleString()}
            </Text>
          </View>
        </Card>
      ) : (
        <Text style={styles.messageText}>No health data available</Text>
      )}

      <View style={styles.buttonContainer}>
        <Button
          title="Add New Data"
          onPress={handleAddData}
          containerStyle={styles.button}
        />
        <Button
          title="Export Data"
          onPress={exportData}
          containerStyle={styles.button}
        />
        <Button
          title="Delete Data"
          onPress={deleteData}
          containerStyle={styles.button}
          buttonStyle={styles.deleteButton}
        />
      </View>

      <Card containerStyle={styles.card}>
        <Card.Title>Privacy Information</Card.Title>
        <Card.Divider />
        <Text style={styles.privacyText}>
          Your health data is protected under HIPAA regulations and stored securely with encryption.
          You can export or delete your data at any time.
        </Text>
      </Card>
    </ScrollView>
  );
}

const useStyles = makeStyles((theme) => ({
  container: {
    flex: 1,
    padding: theme.spacing.md,
  },
  title: {
    marginBottom: theme.spacing.lg,
    color: theme.colors.primary,
  },
  card: {
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    marginBottom: theme.spacing.md,
  },
  errorText: {
    color: theme.colors.error,
    marginBottom: theme.spacing.sm,
    fontSize: theme.fontSize.md,
  },
  loadingText: {
    fontSize: theme.fontSize.md,
    color: theme.colors.grey3,
  },
  messageText: {
    fontSize: theme.fontSize.md,
    color: theme.colors.grey2,
    textAlign: 'center',
  },
  dataText: {
    fontSize: theme.fontSize.md,
    color: theme.colors.text,
    marginBottom: theme.spacing.xs,
  },
  timestamp: {
    fontSize: theme.fontSize.sm,
    color: theme.colors.grey3,
    marginTop: theme.spacing.sm,
  },
  buttonContainer: {
    marginVertical: theme.spacing.lg,
  },
  button: {
    marginVertical: theme.spacing.xs,
  },
  deleteButton: {
    backgroundColor: theme.colors.error,
  },
  privacyText: {
    fontSize: theme.fontSize.sm,
    color: theme.colors.grey2,
    lineHeight: theme.fontSize.lg,
  },
}));
