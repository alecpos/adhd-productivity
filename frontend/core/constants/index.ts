export const API_ENDPOINTS = {
    AUTH: {
        LOGIN: '/auth/login',
        REGISTER: '/auth/register',
        LOGOUT: '/auth/logout'
    },
    TASKS: {
        BASE: '/tasks',
        CREATE: '/tasks/create',
        UPDATE: (id: string) => `/tasks/${id}`
    },
    ENERGY: {
        LOG: '/energy/log',
        PATTERNS: '/energy/patterns',
        INSIGHTS: '/energy/insights'
    }
} as const;

export const ENERGY_LEVELS = {
    LOW: 1,
    MEDIUM: 3,
    HIGH: 5
} as const;

export const TIME_INTERVALS = {
    POMODORO: 25,
    SHORT_BREAK: 5,
    LONG_BREAK: 15,
    HYPERFOCUS_MIN: 45,
    HYPERFOCUS_MAX: 120
} as const;

export const ERROR_MESSAGES = {
    NETWORK_ERROR: 'Network error occurred. Please check your connection.',
    UNAUTHORIZED: 'Please log in to continue.',
    VALIDATION_ERROR: 'Please check your input and try again.',
    SERVER_ERROR: 'Server error occurred. Please try again later.'
} as const; 