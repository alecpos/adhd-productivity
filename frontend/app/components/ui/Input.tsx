import React from 'react';

import { Input as RNEInput, makeStyles, useTheme, Icon } from '@rneui/themed';
import { View, Platform, Text } from 'react-native';

import type { IconProps } from '@rneui/base';
import type { InputProps as RNEInputProps} from '@rneui/themed';
import type { IconNode } from '@rneui/themed/dist/Icon';

type InputVariant = 'default' | 'filled' | 'outline';
type InputSize = 'small' | 'medium' | 'large';

interface InputProps extends Omit<RNEInputProps, 'value' | 'onChangeText'> {
  value: string;
  onChangeText: (text: string) => void;
  variant?: InputVariant;
  size?: InputSize;
  label?: string;
  error?: string;
  hint?: string;
  leftIcon?: IconNode;
  rightIcon?: IconNode;
  onRightIconPress?: () => void;
  isPassword?: boolean;
  fullWidth?: boolean;
}

export const Input: React.FC<InputProps> = ({
  value,
  onChangeText,
  variant = 'default',
  size = 'medium',
  label,
  error,
  hint,
  leftIcon,
  rightIcon,
  onRightIconPress,
  isPassword,
  fullWidth = false,
  disabled,
  ...props
}) => {
  const { theme } = useTheme();
  const styles = useStyles();
  const [showPassword, setShowPassword] = React.useState(!isPassword);

  const getVariantStyles = () => {
    const variants = {
      default: {
        inputContainerStyle: styles.defaultInput,
        inputStyle: styles.defaultInputText,
      },
      filled: {
        inputContainerStyle: styles.filledInput,
        inputStyle: styles.filledInputText,
      },
      outline: {
        inputContainerStyle: styles.outlineInput,
        inputStyle: styles.outlineInputText,
      },
    };
    return variants[variant];
  };

  const getSizeStyles = () => {
    const sizes = {
      small: styles.smallInput,
      medium: styles.mediumInput,
      large: styles.largeInput,
    };
    return sizes[size];
  };

  const renderPasswordIcon = () => (
    <Icon
      name={showPassword ? 'eye-off' : 'eye'}
      type="feather"
      size={20}
      color={theme.colors.grey3}
      onPress={() => setShowPassword(!showPassword)}
    />
  );

  return (
    <View style={[styles.container, fullWidth && styles.fullWidth]}>
      <RNEInput
        value={value}
        onChangeText={onChangeText}
        label={label}
        errorMessage={error}
        errorStyle={styles.errorText}
        disabled={disabled}
        secureTextEntry={isPassword && !showPassword}
        leftIcon={leftIcon ? {
          type: 'feather',
          name: leftIcon,
          color: error ? theme.colors.error : theme.colors.grey3,
        } as Partial<IconProps> : undefined}
        rightIcon={isPassword ? renderPasswordIcon() : rightIcon ? {
          type: 'feather',
          name: rightIcon,
          color: theme.colors.grey3,
          onPress: onRightIconPress,
        } as Partial<IconProps> : undefined}
        {...getVariantStyles()}
        inputContainerStyle={[
          getVariantStyles().inputContainerStyle,
          getSizeStyles(),
          disabled ? styles.disabledInput : undefined,
          error ? styles.errorInput : undefined,
        ]}
        containerStyle={[
          styles.inputContainer,
          fullWidth && styles.fullWidth,
        ]}
        {...props}
      />
      {hint && !error && (
        <Text style={styles.hintText}>{hint}</Text>
      )}
    </View>
  );
};

const useStyles = makeStyles((theme) => ({
  container: {
    marginBottom: 16,
  },
  inputContainer: {
    paddingHorizontal: 0,
  },
  fullWidth: {
    width: '100%',
  },
  // Variant Styles
  defaultInput: {
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.grey4,
  },
  defaultInputText: {
    color: theme.colors.black,
  },
  filledInput: {
    backgroundColor: theme.colors.grey5,
    borderRadius: 8,
    paddingHorizontal: 12,
    borderBottomWidth: 0,
  },
  filledInputText: {
    color: theme.colors.black,
  },
  outlineInput: {
    borderWidth: 1,
    borderColor: theme.colors.grey4,
    borderRadius: 8,
    paddingHorizontal: 12,
  },
  outlineInputText: {
    color: theme.colors.black,
  },
  // Size Styles
  smallInput: {
    height: 40,
  },
  mediumInput: {
    height: 48,
  },
  largeInput: {
    height: 56,
  },
  // State Styles
  errorInput: {
    borderColor: theme.colors.error,
  },
  errorText: {
    color: theme.colors.error,
    fontSize: 12,
    marginTop: 4,
  },
  disabledInput: {
    backgroundColor: theme.colors.grey5,
    borderColor: theme.colors.grey4,
  },
  hintText: {
    color: theme.colors.grey3,
    fontSize: 12,
    marginTop: 4,
  },
}));

export default Input; 