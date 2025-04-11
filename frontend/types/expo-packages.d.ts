declare module 'expo-apple-authentication' {
  export enum AppleAuthenticationScope {
    FULL_NAME = 0,
    EMAIL = 1
  }

  export interface AppleAuthenticationCredential {
    user: string;
    identityToken: string | null;
    fullName: {
      familyName: string | null;
      givenName: string | null;
      middleName: string | null;
      namePrefix: string | null;
      nameSuffix: string | null;
      nickname: string | null;
    } | null;
    email: string | null;
    realUserStatus: number;
    state: string | null;
    authorizationCode: string | null;
  }

  export interface SignInOptions {
    requestedScopes?: AppleAuthenticationScope[];
    state?: string;
  }

  export function signInAsync(options: SignInOptions): Promise<AppleAuthenticationCredential>;
}

declare module 'expo-web-browser' {
  export function maybeCompleteAuthSession(): void;
  export function openAuthSessionAsync(url: string, redirectUrl: string): Promise<any>;
}

declare module 'expo-auth-session/providers/google' {
  export function useAuthRequest(config: any): [any, any, any];
}

declare module 'expo-auth-session' {
  export interface RedirectUriOptions {
    useProxy?: boolean;
    scheme?: string;
    path?: string;
    preferLocalhost?: boolean;
    native?: string;
  }
  export function makeRedirectUri(options?: RedirectUriOptions): string;
}

declare module 'expo-secure-store' {
  export function getItemAsync(key: string): Promise<string | null>;
  export function setItemAsync(key: string, value: string): Promise<void>;
  export function deleteItemAsync(key: string): Promise<void>;
}

declare module 'expo-local-authentication' {
  export function authenticateAsync(options?: any): Promise<{ success: boolean }>;
  export function hasHardwareAsync(): Promise<boolean>;
  export function isEnrolledAsync(): Promise<boolean>;
}

declare module 'expo-crypto' {
  export function getRandomBytesAsync(length: number): Promise<Uint8Array>;
  export function digestStringAsync(algorithm: string, data: string): Promise<string>;
}

declare module 'expo-sharing' {
  export function shareAsync(url: string, options?: any): Promise<void>;
  export function isAvailableAsync(): Promise<boolean>;
}
