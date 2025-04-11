import type { AxiosError, AxiosResponse } from 'axios';

export interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
}

export interface ApiError {
  status: number;
  message: string;
  details?: Record<string, unknown>;
}

export type ApiResult<T> = Promise<ApiResponse<T>>;

export function isAxiosError(error: unknown): error is AxiosError {
  return (error as AxiosError)?.isAxiosError === true;
}

export function getErrorMessage(error: unknown): string {
  if (isAxiosError(error)) {
    return (error.response?.data as ApiError)?.message || error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return String(error);
}

export function getApiResponse<T>(response: AxiosResponse): ApiResponse<T> {
  return {
    data: response.data,
    status: response.status,
    message: (response.data as { message?: string })?.message
  };
}

export function handleApiError(error: unknown): never {
  const message = getErrorMessage(error);
  throw new Error(message);
}
