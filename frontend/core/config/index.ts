export interface Config {
  API_URL: string;
  API_TIMEOUT: number;
}

const config: Config = {
  API_URL: process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000',
  API_TIMEOUT: 10000,
};

export default config; 