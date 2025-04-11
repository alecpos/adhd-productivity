// Default configuration for development
const defaultConfig = {
  logger: {
    log(level: number, message: string) {
      if (level >= 2) { // Warning level or higher
        console.log(message);
      }
    }
  }
};

// Initialize the client with default configuration
let configCatClient: any = null;

import("configcat-js").then(configcat => {
  const sdkKey = process.env.EXPO_PUBLIC_CONFIGCAT_SDK_KEY || '';
  if (!sdkKey) {
    console.warn('ConfigCat SDK key is not set. Feature flags will default to false.');
    return;
  }

  try {
    // Use specific polling mode parameters that are valid for web
    configCatClient = configcat.getClient(sdkKey, {
      // For web use auto polling mode
      pollIntervalSeconds: 60,
      logger: defaultConfig.logger,
      // Don't include a pollingMode parameter
    });
  } catch (error) {
    console.error('Failed to initialize ConfigCat:', error);
  }
}).catch(error => {
  console.error('Failed to import ConfigCat:', error);
});

// Helper function to get feature flag value with type safety
export async function getFeatureFlag(key: string, defaultValue: boolean = false): Promise<boolean> {
  try {
    if (!configCatClient) {
      console.warn('ConfigCat client not initialized yet');
      return defaultValue;
    }
    return await configCatClient.getValueAsync(key, defaultValue);
  } catch (error: unknown) {
    console.warn(`Error getting feature flag ${key}:`, error);
    return defaultValue;
  }
}

// Helper function to get feature flag value with a synchronous interface
// Note: This still uses getValueAsync internally but provides a default value immediately
export function getFeatureFlagSync(key: string, defaultValue: boolean = false): boolean {
  // Return default value if client is not initialized
  if (!configCatClient) {
    console.warn('ConfigCat client not initialized yet');
    return defaultValue;
  }

  // Return default value immediately
  const value = defaultValue;

  // Fetch the actual value asynchronously for next render
  configCatClient.getValueAsync(key, defaultValue)
    .then((actualValue: boolean) => {
      if (actualValue !== value) {
        // Log if there's a mismatch between default and actual value
        console.debug(`Feature flag ${key} value updated from ${value} to ${actualValue}`);
      }
    })
    .catch((error: unknown) => {
      console.warn(`Error getting feature flag ${key}:`, error);
    });

  return value;
}

// Export a function to get the client, which will wait for initialization if needed
export async function getConfigCatClient() {
  if (!configCatClient) {
    await new Promise(resolve => {
      const checkInterval = setInterval(() => {
        if (configCatClient) {
          clearInterval(checkInterval);
          resolve(configCatClient);
        }
      }, 100);
    });
  }
  return configCatClient;
}
