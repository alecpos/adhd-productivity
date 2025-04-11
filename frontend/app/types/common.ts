export type UUID = string;

export interface BaseResponse {
    success: boolean;
    message?: string;
}

export interface ErrorResponse extends BaseResponse {
    success: false;
    error: string;
}

// Export types and constants
export const CommonTypesConstants = {
    UUID: String,
    BaseResponse: {} as BaseResponse,
    ErrorResponse: {} as ErrorResponse,
} as const;

// Export a dummy component for the router
export default function CommonTypesComponent() {
    return null;
}
