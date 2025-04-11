export interface User {
  id: string;
  email: string;
  name?: string;
  preferences?: {
    theme?: 'light' | 'dark';
    timezone?: string;
    defaultView?: 'day' | 'week' | 'month';
  };
  connectedCalendars?: {
    google?: boolean;
    outlook?: boolean;
    apple?: boolean;
  };
}

export interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  error: Error | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  signup: (email: string, password: string, name?: string) => Promise<void>;
  resetPassword: (email: string) => Promise<void>;
  updateUser: (data: Partial<User>) => Promise<void>;
}
