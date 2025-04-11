import type { UUID } from './common';

export interface User {
    id: UUID;
    username: string;
    email: string;
    name?: string;
    calendar_connected: boolean;
    calendar_settings?: {
        provider?: 'google' | 'apple' | 'outlook';
        settings?: Record<string, any>;
    };
}
