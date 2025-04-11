declare module 'configcat-js' {
  interface IConfigCatClient {
    getValue(key: string, defaultValue: any): Promise<any>;
    getValueAsync<T>(key: string, defaultValue: T): Promise<T>;
    forceRefresh(): Promise<void>;
  }

  interface IConfigCatOptions {
    pollIntervalSeconds?: number;
    maxInitWaitTimeSeconds?: number;
    configChanged?: () => void;
    logger?: any;
  }

  export function createClient(
    sdkKey: string,
    options?: IConfigCatOptions
  ): IConfigCatClient;

  export function getClient(
    sdkKey: string,
    options?: IConfigCatOptions
  ): IConfigCatClient;

  export function createConsoleLogger(level: number): any;
}
