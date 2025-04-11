import React, { useState } from 'react';

import { Text, Icon, makeStyles, useTheme } from '@rneui/themed';
import * as ImagePicker from 'expo-image-picker';
import { View, Image, TouchableOpacity } from 'react-native';

import { ActionSheet } from './ActionSheet';

interface ImagePickerProps {
  onImageSelected: (uri: string) => void;
  value?: string;
  label?: string;
}

export const CustomImagePicker: React.FC<ImagePickerProps> = ({
  onImageSelected,
  value,
  label = 'Select Image',
}) => {
  const [showOptions, setShowOptions] = useState(false);
  const styles = useStyles();

  const requestPermission = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      alert('Sorry, we need camera roll permissions to make this work!');
      return false;
    }
    return true;
  };

  const handleCamera = async () => {
    const hasPermission = await requestPermission();
    if (!hasPermission) return;

    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [4, 3],
      quality: 1,
    });

    if (!result.canceled) {
      onImageSelected(result.assets[0].uri);
    }
    setShowOptions(false);
  };

  const handleGallery = async () => {
    const hasPermission = await requestPermission();
    if (!hasPermission) return;

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [4, 3],
      quality: 1,
    });

    if (!result.canceled) {
      onImageSelected(result.assets[0].uri);
    }
    setShowOptions(false);
  };

  return (
    <View style={styles.container}>
      <TouchableOpacity
        style={styles.picker}
        onPress={() => setShowOptions(true)}
      >
        {value ? (
          <Image source={{ uri: value }} style={styles.image} />
        ) : (
          <>
            <Icon name="image" type="material" style={styles.icon} />
            <Text style={styles.label}>{label}</Text>
          </>
        )}
      </TouchableOpacity>

      <ActionSheet
        visible={showOptions}
        onClose={() => setShowOptions(false)}
        options={[
          {
            label: 'Take Photo',
            onPress: handleCamera,
            icon: 'camera',
          },
          {
            label: 'Choose from Gallery',
            onPress: handleGallery,
            icon: 'image',
          },
        ]}
      />
    </View>
  );
};

const useStyles = makeStyles((theme) => ({
  container: {
    marginBottom: theme.spacing.md,
  },
  picker: {
    height: 200,
    borderWidth: 1,
    borderColor: theme.colors.grey4,
    borderRadius: theme.borderRadius.md,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: theme.colors.grey5,
    overflow: 'hidden',
  },
  image: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  icon: {
    marginBottom: theme.spacing.sm,
    color: theme.colors.grey2,
  },
  label: {
    color: theme.colors.grey2,
    fontSize: theme.fontSize.md,
  },
}));
