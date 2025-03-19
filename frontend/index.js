import { registerRootComponent } from 'expo';
import { Platform } from 'react-native';
import Constants from 'expo-constants';

// For web, use our simplified app that doesn't rely on problematic native modules
let App;
if (Platform.OS === 'web' && Constants.expoConfig?.extra?.useSimpleWebApp) {
  // Use the web-specific app when running on web
  App = require('./App.web').default;
} else {
  // Use expo-router for native platforms
  App = require('expo-router/entry');
}

registerRootComponent(App); 