export type UUID = string; 

export interface BaseResponse {
  success: boolean;
  message: string;
  data?: any;
} 

export type ApiResponse<T> = {
  data: T;
  status: number;
  message?: string;
  error?: Error;
};

export type ErrorResponse = {
  status: number;
  message: string;
  error?: Error;
};

export type UnknownRecord = Record<string, unknown>; 