module.exports = {
  name: 'ADHD Calendar',
  slug: 'adhd-calendar',
  version: '1.0.0',
  orientation: 'portrait',
  icon: './assets/images/icon.png',
  userInterfaceStyle: 'light',
  splash: {
    image: './assets/images/splash-icon.png',
    resizeMode: 'contain',
    backgroundColor: '#4782DA'
  },
  assetBundlePatterns: ['**/*'],
  ios: {
    supportsTablet: true,
    bundleIdentifier: 'com.adhd.calendar'
  },
  android: {
    adaptiveIcon: {
      foregroundImage: './assets/images/adaptive-icon.png',
      backgroundColor: '#4782DA'
    },
    package: 'com.adhd.calendar'
  },
  web: {
    favicon: './assets/images/favicon.png',
    bundler: 'metro',
    output: 'static',
    build: {
      babel: {
        dangerouslyAddModulePathsToTranspile: [
          'expo-haptics',
          'expo-notifications',
          'expo-apple-authentication',
          'expo-local-authentication'
        ]
      }
    }
  },
  plugins: [
    'expo-router',
    'expo-font',
    'expo-secure-store'
  ],
  extra: {
    useSimpleWebApp: process.env.EXPO_TARGET === 'web',
    skipProblematicModules: process.env.EXPO_TARGET === 'web'
  }
};
