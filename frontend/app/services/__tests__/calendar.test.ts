// Mock Expo modules before imports
jest.mock('expo-apple-authentication', () => ({
    AppleAuthenticationScope: {
        FULL_NAME: 'full_name',
        EMAIL: 'email'
    },
    signInAsync: jest.fn()
}));

jest.mock('expo-web-browser', () => ({
    maybeCompleteAuthSession: jest.fn(),
    openAuthSessionAsync: jest.fn()
}));

jest.mock('expo-auth-session', () => ({
    makeRedirectUri: jest.fn(() => 'mock-redirect-uri')
}));

// Regular imports
import * as AppleAuthentication from 'expo-apple-authentication';
import * as WebBrowser from 'expo-web-browser';
import { Platform } from 'react-native';

import { EventType, RecurrenceType } from '../../types/calendar';
import api from '../api';
import { calendarService } from '../calendar';


import type { CalendarEvent } from '../../types/calendar';

// Mock dependencies
jest.mock('../api');
jest.mock('react-native', () => ({
    Platform: {
        OS: 'ios'
    }
}));

describe('CalendarService', () => {
    beforeEach(async () => {
        // Reset all mocks before each test
        jest.clearAllMocks();
        // Reset calendar service state
        await calendarService.disconnectCalendar('test-user').catch(() => {
            // Ignore disconnection errors in test setup
        });
    });

    describe('Provider Status', () => {
        it('should initially have no provider and not be connected', () => {
            expect(calendarService.getCurrentProvider()).toBeUndefined();
            expect(calendarService.isConnected()).toBe(false);
        });

        it('should update provider status after successful Google connection', async () => {
            const mockToken = 'mock-google-token';
            (api.post as jest.Mock).mockResolvedValueOnce({});

            await calendarService.setGoogleToken(mockToken);

            expect(calendarService.getCurrentProvider()).toBe('google');
            expect(calendarService.isConnected()).toBe(true);
        });

        it('should handle Google connection failure', async () => {
            const mockToken = 'mock-google-token';
            const mockError = new Error('Connection failed');
            (api.post as jest.Mock).mockRejectedValueOnce(mockError);

            await expect(calendarService.setGoogleToken(mockToken)).rejects.toThrow('Connection failed');
            expect(calendarService.getCurrentProvider()).toBeUndefined();
            expect(calendarService.isConnected()).toBe(false);
        });
    });

    describe('Apple Calendar Integration', () => {
        it('should connect to Apple Calendar successfully', async () => {
            const mockCredential = {
                user: 'test-user',
                email: 'test@example.com',
                identityToken: 'mock-token',
                fullName: { givenName: 'Test', familyName: 'User' }
            };

            (AppleAuthentication.signInAsync as jest.Mock).mockResolvedValueOnce(mockCredential);
            (api.post as jest.Mock)
                .mockResolvedValueOnce({}) // For disconnect
                .mockResolvedValueOnce({}) // For settings update
                .mockResolvedValueOnce({}); // For token exchange

            const result = await calendarService.connectAppleCalendar();

            expect(result).toBe(true);
            expect(calendarService.getCurrentProvider()).toBe('apple');
            expect(calendarService.isConnected()).toBe(true);
            expect(api.post).toHaveBeenCalledWith('/calendar/settings', {
                provider: 'apple',
                settings: { identity_token: 'mock-token', user_id: 'test-user' }
            });
        });

        it('should handle Apple Calendar connection failure', async () => {
            const mockError = new Error('Apple auth failed');
            (AppleAuthentication.signInAsync as jest.Mock).mockRejectedValueOnce(mockError);

            await expect(calendarService.connectAppleCalendar()).rejects.toThrow('Apple auth failed');
            expect(calendarService.getCurrentProvider()).toBeUndefined();
            expect(calendarService.isConnected()).toBe(false);
        });

        it('should prevent Apple Calendar connection on non-iOS devices', async () => {
            // Mock Platform.OS directly
            const originalPlatform = Platform.OS;
            Platform.OS = 'android';

            const result = await calendarService.connectAppleCalendar();

            expect(result).toBe(false);
            expect(calendarService.getCurrentProvider()).toBeUndefined();
            expect(calendarService.isConnected()).toBe(false);

            // Restore Platform.OS
            Platform.OS = originalPlatform;
        });

        it('should handle Apple token exchange failure', async () => {
            const mockCredential = {
                user: 'test-user',
                email: 'test@example.com',
                identityToken: 'mock-token',
                fullName: { givenName: 'Test', familyName: 'User' }
            };
            const mockError = new Error('Token exchange failed');

            (AppleAuthentication.signInAsync as jest.Mock).mockResolvedValueOnce(mockCredential);
            (api.post as jest.Mock)
                .mockResolvedValueOnce({}) // For disconnect
                .mockRejectedValueOnce(mockError); // For settings update

            await expect(calendarService.connectAppleCalendar()).rejects.toThrow('Token exchange failed');
            expect(calendarService.getCurrentProvider()).toBeUndefined();
            expect(calendarService.isConnected()).toBe(false);
        });
    });

    describe('Outlook Calendar Integration', () => {
        it('should connect to Outlook Calendar successfully', async () => {
            const mockCode = 'mock-auth-code';
            const mockAccessToken = 'mock-access-token';

            // Mock successful auth session
            (WebBrowser.openAuthSessionAsync as jest.Mock).mockResolvedValueOnce({
                type: 'success',
                url: `adhd-calendar://outlook-auth?code=${mockCode}`
            });

            // Mock token exchange
            (api.post as jest.Mock).mockResolvedValueOnce({
                data: { access_token: mockAccessToken }
            }).mockResolvedValueOnce({}); // For settings update

            const result = await calendarService.connectOutlookCalendar();

            expect(result).toBe(true);
            expect(calendarService.getCurrentProvider()).toBe('outlook');
            expect(calendarService.isConnected()).toBe(true);
            expect(api.post).toHaveBeenCalledWith('/calendar/outlook/token', expect.any(Object));
            expect(api.post).toHaveBeenCalledWith('/calendar/settings', {
                provider: 'outlook',
                settings: { access_token: mockAccessToken }
            });
        });

        it('should handle Outlook auth session cancellation', async () => {
            (WebBrowser.openAuthSessionAsync as jest.Mock).mockResolvedValueOnce({
                type: 'cancel'
            });

            const result = await calendarService.connectOutlookCalendar();

            expect(result).toBe(false);
            expect(calendarService.getCurrentProvider()).toBeUndefined();
            expect(calendarService.isConnected()).toBe(false);
        });

        it('should handle Outlook token exchange failure', async () => {
            const mockCode = 'mock-auth-code';
            const mockError = new Error('Token exchange failed');

            (WebBrowser.openAuthSessionAsync as jest.Mock).mockResolvedValueOnce({
                type: 'success',
                url: `adhd-calendar://outlook-auth?code=${mockCode}`
            });

            (api.post as jest.Mock).mockRejectedValueOnce(mockError);

            await expect(calendarService.connectOutlookCalendar()).rejects.toThrow('Token exchange failed');
            expect(calendarService.getCurrentProvider()).toBeUndefined();
            expect(calendarService.isConnected()).toBe(false);
        });
    });

    describe('Calendar Event Management', () => {
        const mockEvent: CalendarEvent = {
            title: 'Test Event',
            description: 'Test Description',
            start_time: new Date('2024-01-01T10:00:00Z'),
            end_time: new Date('2024-01-01T11:00:00Z'),
            event_type: EventType.MEETING,
            is_all_day: false,
            recurrence_type: RecurrenceType.NONE
        };

        beforeEach(() => {
            // Set up Google connection for event tests
            (api.post as jest.Mock).mockResolvedValueOnce({});
            return calendarService.setGoogleToken('mock-token');
        });

        it('should create a calendar event successfully', async () => {
            const mockEventId = 'mock-event-id';
            (api.post as jest.Mock).mockResolvedValueOnce({ data: { event_id: mockEventId } });

            const result = await calendarService.createCalendarEvent(mockEvent);

            expect(result).toBe(mockEventId);
            expect(api.post).toHaveBeenCalledWith('/calendar/events', expect.objectContaining({
                title: mockEvent.title,
                description: mockEvent.description
            }));
        });

        it('should handle event creation failure', async () => {
            const mockError = new Error('Failed to create event');
            (api.post as jest.Mock).mockRejectedValueOnce(mockError);

            await expect(calendarService.createCalendarEvent(mockEvent)).rejects.toThrow('Failed to create event');
        });

        it('should update a calendar event successfully', async () => {
            const eventId = 'test-event-id';
            const updates = {
                title: 'Updated Title',
                description: 'Updated Description'
            };
            (api.put as jest.Mock).mockResolvedValueOnce({});

            await calendarService.updateCalendarEvent(eventId, updates);

            expect(api.put).toHaveBeenCalledWith(`/calendar/events/${eventId}`, expect.objectContaining(updates));
        });

        it('should handle event update failure', async () => {
            const eventId = 'test-event-id';
            const updates = { title: 'Updated Title' };
            const mockError = new Error('Failed to update event');
            (api.put as jest.Mock).mockRejectedValueOnce(mockError);

            await expect(calendarService.updateCalendarEvent(eventId, updates)).rejects.toThrow('Failed to update event');
        });

        it('should delete a calendar event successfully', async () => {
            const eventId = 'test-event-id';
            (api.delete as jest.Mock).mockResolvedValueOnce({});

            await calendarService.deleteCalendarEvent(eventId);

            expect(api.delete).toHaveBeenCalledWith(`/calendar/events/${eventId}`);
        });

        it('should handle event deletion failure', async () => {
            const eventId = 'test-event-id';
            const mockError = new Error('Failed to delete event');
            (api.delete as jest.Mock).mockRejectedValueOnce(mockError);

            await expect(calendarService.deleteCalendarEvent(eventId)).rejects.toThrow('Failed to delete event');
        });

        it('should fetch calendar events successfully', async () => {
            const mockEvents = [
                { id: '1', title: 'Event 1' },
                { id: '2', title: 'Event 2' }
            ];
            (api.get as jest.Mock).mockResolvedValueOnce({ data: mockEvents });

            const result = await calendarService.getCalendarEvents('user-id');

            expect(result).toStrictEqual(mockEvents);
            expect(api.get).toHaveBeenCalledWith('/calendar/events', expect.any(Object));
        });

        it('should handle event fetching failure', async () => {
            const mockError = new Error('Failed to fetch events');
            (api.get as jest.Mock).mockRejectedValueOnce(mockError);

            await expect(calendarService.getCalendarEvents('user-id')).rejects.toThrow('Failed to fetch events');
        });
    });

    describe('Calendar Sync', () => {
        beforeEach(() => {
            // Set up Google connection for sync tests
            (api.post as jest.Mock).mockResolvedValueOnce({});
            return calendarService.setGoogleToken('mock-token');
        });

        it('should sync calendar successfully', async () => {
            (api.post as jest.Mock).mockResolvedValueOnce({});

            await calendarService.sync('user-id');

            expect(api.post).toHaveBeenCalledWith('/calendar/sync', { user_id: 'user-id' });
        });

        it('should handle sync failure', async () => {
            const mockError = new Error('Sync failed');
            (api.post as jest.Mock).mockRejectedValueOnce(mockError);

            await expect(calendarService.sync('user-id')).rejects.toThrow('Sync failed');
        });

        it('should handle sync with no provider connected', async () => {
            await calendarService.disconnectCalendar('user-id');

            await expect(calendarService.sync('user-id')).rejects.toThrow('No calendar provider connected');
        });
    });

    describe('Disconnection', () => {
        it('should clear provider state after disconnection', async () => {
            // First connect to a provider
            const mockToken = 'mock-google-token';
            (api.post as jest.Mock).mockResolvedValueOnce({});
            await calendarService.setGoogleToken(mockToken);

            // Then disconnect
            (api.post as jest.Mock).mockResolvedValueOnce({});
            await calendarService.disconnectCalendar('test-user');

            expect(calendarService.getCurrentProvider()).toBeUndefined();
            expect(calendarService.isConnected()).toBe(false);
        });

        it('should handle disconnection failure', async () => {
            const mockError = new Error('Disconnection failed');
            (api.post as jest.Mock).mockRejectedValueOnce(mockError);

            await expect(calendarService.disconnectCalendar('test-user')).rejects.toThrow('Disconnection failed');
        });
    });

    describe('Calendar Event Filtering', () => {
        const mockEvent: CalendarEvent = {
            title: 'Test Event',
            description: 'Test Description',
            start_time: new Date('2024-01-01T10:00:00Z'),
            end_time: new Date('2024-01-01T11:00:00Z'),
            event_type: EventType.MEETING,
            is_all_day: false,
            recurrence_type: RecurrenceType.NONE
        };

        beforeEach(() => {
            // Set up Google connection for event tests
            (api.post as jest.Mock).mockResolvedValueOnce({});
            return calendarService.setGoogleToken('mock-token');
        });

        it('should fetch events with date range filter', async () => {
            const mockEvents = [
                { id: '1', title: 'Event 1', start_time: '2024-01-01T10:00:00Z' },
                { id: '2', title: 'Event 2', start_time: '2024-01-02T10:00:00Z' }
            ];
            const startDate = new Date('2024-01-01');
            const endDate = new Date('2024-01-03');

            (api.get as jest.Mock).mockResolvedValueOnce({ data: mockEvents });

            const result = await calendarService.getCalendarEvents('user-id', startDate, endDate);

            expect(result).toStrictEqual(mockEvents);
            expect(api.get).toHaveBeenCalledWith('/calendar/events', {
                params: {
                    user_id: 'user-id',
                    start_date: startDate.toISOString(),
                    end_date: endDate.toISOString(),
                    include_external: true
                }
            });
        });

        it('should handle recurring events correctly', async () => {
            const mockRecurringEvent: CalendarEvent = {
                ...mockEvent,
                recurrence_type: RecurrenceType.WEEKLY,
                recurrence_end: new Date('2024-02-01')
            };

            (api.post as jest.Mock).mockResolvedValueOnce({ data: { event_id: 'recurring-event-id' } });

            const result = await calendarService.createCalendarEvent(mockRecurringEvent);

            expect(result).toBe('recurring-event-id');
            expect(api.post).toHaveBeenCalledWith('/calendar/events', {
                ...mockRecurringEvent,
                start_time: (mockRecurringEvent.start_time as Date).toISOString(),
                end_time: (mockRecurringEvent.end_time as Date).toISOString(),
                recurrence_end: (mockRecurringEvent.recurrence_end as Date).toISOString()
            });
        });

        it('should handle all-day events correctly', async () => {
            const mockAllDayEvent: CalendarEvent = {
                ...mockEvent,
                is_all_day: true,
                start_time: new Date('2024-01-01'),
                end_time: new Date('2024-01-02')
            };

            (api.post as jest.Mock).mockResolvedValueOnce({ data: { event_id: 'all-day-event-id' } });

            const result = await calendarService.createCalendarEvent(mockAllDayEvent);

            expect(result).toBe('all-day-event-id');
            expect(api.post).toHaveBeenCalledWith('/calendar/events', {
                ...mockAllDayEvent,
                start_time: (mockAllDayEvent.start_time as Date).toISOString(),
                end_time: (mockAllDayEvent.end_time as Date).toISOString()
            });
        });
    });
});
