export class AppError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode?: number
  ) {
    super(message);
    this.name = 'AppError';
    Object.setPrototypeOf(this, AppError.prototype);
  }
}

export const AUTH_ERROR_CODES = {
  INVALID_CREDENTIALS: 'INVALID_CREDENTIALS',
  USER_NOT_FOUND: 'USER_NOT_FOUND',
  EMAIL_EXISTS: 'EMAIL_EXISTS',
  NETWORK_ERROR: 'NETWORK_ERROR',
  UNKNOWN_ERROR: 'UNKNOWN_ERROR',
  AUTH_ERROR: 'AUTH_ERROR'
} as const;

export type AuthErrorCode = keyof typeof AUTH_ERROR_CODES;

export interface ApiErrorResponse {
  message: string;
  code: AuthErrorCode;
  statusCode: number;
}
