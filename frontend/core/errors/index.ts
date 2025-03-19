export class AppError extends Error {
    constructor(
        message: string,
        public code: string,
        public details?: any
    ) {
        super(message);
        this.name = 'AppError';
    }
}

export const errorHandler = (error: any): AppError => {
    // Convert various error types to AppError
    if (error instanceof AppError) return error;
    
    if (error.response) {
        // API error response
        return new AppError(
            error.response.data.message || 'API Error',
            error.response.status.toString(),
            error.response.data
        );
    }
    
    if (error.request) {
        // Network error
        return new AppError(
            'Network Error',
            'NETWORK_ERROR',
            error.request
        );
    }
    
    // Default error
    return new AppError(
        error.message || 'An unknown error occurred',
        'UNKNOWN_ERROR',
        error
    );
}; 