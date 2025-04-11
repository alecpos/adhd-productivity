const React = require('react');

const mockComponent = (name) => {
  const component = ({ children, testID, ...props }) => {
    return React.createElement('View', { testID, ...props }, children);
  };
  component.displayName = name;
  return component;
};

module.exports = {
  View: mockComponent('View'),
  Text: mockComponent('Text'),
  ScrollView: mockComponent('ScrollView'),
  TouchableOpacity: mockComponent('TouchableOpacity'),
  TouchableWithoutFeedback: mockComponent('TouchableWithoutFeedback'),
  ActivityIndicator: mockComponent('ActivityIndicator'),
  Modal: mockComponent('Modal'),
  Pressable: mockComponent('Pressable'),
  Image: mockComponent('Image'),
  TextInput: mockComponent('TextInput'),
  Animated: {
    View: mockComponent('Animated.View'),
    createAnimatedComponent: (component) => component,
    timing: () => ({
      start: (callback) => callback && callback(),
    }),
    spring: () => ({
      start: (callback) => callback && callback(),
    }),
    Value: function (value) {
      this.setValue = (newValue) => {
        value = newValue;
      };
    },
  },
  Platform: {
    OS: 'ios',
    select: (obj) => obj.ios,
  },
  StyleSheet: {
    create: (styles) => styles,
    hairlineWidth: 1,
  },
  Dimensions: {
    get: () => ({
      width: 375,
      height: 812,
    }),
  },
};
