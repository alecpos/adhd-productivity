export const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

// API endpoints
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/api/auth/login',
    REGISTER: '/api/auth/register',
    LOGOUT: '/api/auth/logout',
    VERIFY: '/api/auth/verify'
  },
  TASKS: {
    BASE: '/api/tasks',
    CREATE: '/api/tasks/create',
    UPDATE: (id: string) => `/api/tasks/${id}`
  },
  ENERGY: {
    LOG: '/api/energy/log',
    PATTERNS: '/api/energy/patterns',
    INSIGHTS: '/api/energy/insights'
  },
  HEALTH: {
    DATA: '/api/health/data',
    EXPORT: '/api/health/export',
    IMPORT: '/api/health/import',
    SYNC: '/api/health/sync'
  },
  MENTAL_HEALTH: {
    BASE: '/api/mental-health',
    LOGS: '/api/mental-health/logs',
    STATS: (userId: string) => `/api/mental-health/stats/${userId}`,
    INSIGHTS: (userId: string) => `/api/mental-health/insights/${userId}`,
    TRENDS: '/api/mental-health/trends',
    ANALYZE: '/api/mental-health/analyze',
    RECOMMENDATIONS: '/api/mental-health/recommendations',
    COPING_STRATEGIES: '/api/mental-health/coping-strategies'
  },
  CALENDAR: {
    BASE: '/api/calendar',
    EVENTS: '/api/calendar/events',
    EVENT: (id: string) => `/api/calendar/events/${id}`,
    USER_EVENTS: (userId: string) => `/api/calendar/events/${userId}`,
    SETTINGS: (userId: string) => `/api/calendar/settings/${userId}`,
    SYNC: (userId: string) => `/api/calendar/sync/${userId}`,
    AVAILABLE_SLOTS: (userId: string) => `/api/calendar/available-slots/${userId}`
  }
} as const;

