import type { ApiError } from '../types/api';
import type { AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios';

export function createMockApiError(
  status: number,
  message: string,
  details?: Record<string, unknown>
): AxiosError<ApiError> {
  const apiError: ApiError = { status, message, details };
  
  const error = new Error(message) as AxiosError<ApiError>;
  error.code = 'ERR_BAD_REQUEST';
  error.name = 'AxiosError';
  error.response = {
    data: {
      detail: message,
      ...apiError
    },
    status,
    statusText: message,
    headers: {},
    config: {
      url: '/api/test',
      method: 'POST',
      headers: {}
    } as AxiosRequestConfig
  } as AxiosResponse<ApiError>;
  
  return error;
}

export function expectError(error: unknown, expectedMessage: string): void {
  expect(error).toBeDefined();
  if (error instanceof Error) {
    expect(error.message).toBe(expectedMessage);
  } else {
    fail('Expected error to be an instance of Error');
  }
}

export function expectApiError(
  error: unknown,
  expectedStatus: number,
  expectedMessage: string
): void {
  expect(error).toBeDefined();
  expect(error).toBeInstanceOf(Error);
  const axiosError = error as AxiosError<ApiError>;
  expect(axiosError.response?.status).toBe(expectedStatus);
  expect(axiosError.response?.data.message).toBe(expectedMessage);
}

export async function expectAsyncError(
  promise: Promise<unknown>,
  expectedMessage: string
): Promise<void> {
  try {
    await promise;
    fail('Expected promise to reject');
  } catch (error) {
    expectError(error, expectedMessage);
  }
}

export async function expectAsyncApiError(
  promise: Promise<unknown>,
  expectedStatus: number,
  expectedMessage: string
): Promise<void> {
  try {
    await promise;
    fail('Expected promise to reject');
  } catch (error) {
    expectApiError(error, expectedStatus, expectedMessage);
  }
} 