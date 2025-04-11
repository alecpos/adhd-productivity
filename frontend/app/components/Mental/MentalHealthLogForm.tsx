import React, { useState } from 'react';

import { Input, Button, makeStyles, Text } from '@rneui/themed';
import { View } from 'react-native';

import type { CreateMentalHealthLog } from '@/app/types/mental-health';

interface MentalHealthLogFormProps {
  onSubmit: (data: Partial<CreateMentalHealthLog>) => Promise<void>;
  quickMode?: boolean;
  onSuccess?: () => void;
}

const MentalHealthLogForm: React.FC<MentalHealthLogFormProps> = ({
  onSubmit,
  quickMode = false,
  onSuccess
}) => {
  const [formData, setFormData] = useState<Partial<CreateMentalHealthLog>>({
    moodScore: 3,
    stressLevel: 0,
    anxietyLevel: 0,
    focusLevel: 3,
    notes: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const styles = useStyles();

  const isFormValid = () => {
    const isValidScore = (score: number | undefined) =>
      score !== undefined && score >= 0 && score <= 10;

    return (
      isValidScore(formData.moodScore) &&
      isValidScore(formData.stressLevel) &&
      isValidScore(formData.anxietyLevel) &&
      (!formData.focusLevel || isValidScore(formData.focusLevel))
    );
  };

  const handleChange = (field: keyof CreateMentalHealthLog, value: any) => {
    console.debug(`Updating ${field}:`, value);
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    setError(null);
  };

  const handleSubmit = async () => {
    console.debug('Submitting form data:', formData);
    setLoading(true);
    setError(null);
    try {
      await onSubmit(formData);
      console.debug('Form submitted successfully');
      setFormData({
        moodScore: 3,
        stressLevel: 0,
        anxietyLevel: 0,
        focusLevel: 3,
        notes: ''
      });
      onSuccess?.();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to submit log';
      console.error('Error submitting mental health log:', err);
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Input
        label="Mood Score (0-10)"
        placeholder="How are you feeling? (0-10)"
        value={formData.moodScore?.toString()}
        onChangeText={(value) => {
          const score = parseInt(value);
          if (!isNaN(score) && score >= 0 && score <= 10) {
            handleChange('moodScore', score);
          }
        }}
        keyboardType="numeric"
        errorMessage={formData.moodScore !== undefined && (formData.moodScore < 0 || formData.moodScore > 10) ? 'Score must be between 0 and 10' : undefined}
      />
      <Input
        label="Stress Level (0-10)"
        placeholder="Current stress level (0-10)"
        value={formData.stressLevel?.toString()}
        onChangeText={(value) => {
          const level = parseInt(value);
          if (!isNaN(level) && level >= 0 && level <= 10) {
            handleChange('stressLevel', level);
          }
        }}
        keyboardType="numeric"
        errorMessage={formData.stressLevel !== undefined && (formData.stressLevel < 0 || formData.stressLevel > 10) ? 'Level must be between 0 and 10' : undefined}
      />
      <Input
        label="Anxiety Level (0-10)"
        placeholder="Current anxiety level (0-10)"
        value={formData.anxietyLevel?.toString()}
        onChangeText={(value) => {
          const level = parseInt(value);
          if (!isNaN(level) && level >= 0 && level <= 10) {
            handleChange('anxietyLevel', level);
          }
        }}
        keyboardType="numeric"
        errorMessage={formData.anxietyLevel !== undefined && (formData.anxietyLevel < 0 || formData.anxietyLevel > 10) ? 'Level must be between 0 and 10' : undefined}
      />
      {!quickMode && (
        <>
          <Input
            label="Focus Level (0-10)"
            placeholder="Current focus level (0-10)"
            value={formData.focusLevel?.toString()}
            onChangeText={(value) => {
              const level = parseInt(value);
              if (!isNaN(level) && level >= 0 && level <= 10) {
                handleChange('focusLevel', level);
              }
            }}
            keyboardType="numeric"
            errorMessage={formData.focusLevel !== undefined && (formData.focusLevel < 0 || formData.focusLevel > 10) ? 'Level must be between 0 and 10' : undefined}
          />
          <Input
            label="Notes"
            placeholder="Any additional notes?"
            value={formData.notes}
            onChangeText={(value) => handleChange('notes', value)}
            multiline
          />
        </>
      )}
      {error && (
        <Text style={styles.error}>{error}</Text>
      )}
      <Button
        title="Log Mood"
        onPress={handleSubmit}
        loading={loading}
        disabled={loading || !isFormValid()}
      />
    </View>
  );
};

const useStyles = makeStyles((theme) => ({
  container: {
    padding: theme.spacing.md,
  },
  error: {
    color: theme.colors.error,
    marginBottom: theme.spacing.sm,
    textAlign: 'center',
  },
}));

export default MentalHealthLogForm;
