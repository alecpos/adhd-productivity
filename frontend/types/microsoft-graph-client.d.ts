declare module '@microsoft/microsoft-graph-client' {
  export interface AuthProvider {
    (done: (error: any, accessToken: string) => void): void;
  }

  export interface GraphRequestCallback {
    (error: any, response: any): void;
  }

  export interface Client {
    api(path: string): any;
    init(options: { authProvider: AuthProvider }): Client;
  }

  export const Client: {
    init(options: { authProvider: AuthProvider }): Client;
  };
} 