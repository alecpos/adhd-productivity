import React, { useState } from 'react';

import { Text } from '@rneui/themed';
import { makeRedirectUri } from 'expo-auth-session';
import * as Google from 'expo-auth-session/providers/google';
import * as WebBrowser from 'expo-web-browser';
import { View, StyleSheet } from 'react-native';
import Toast from 'react-native-toast-message';

import { calendarService } from '@/app/services/calendar';


import { AnimatedButton } from '../../components/ui/AnimatedButton';

WebBrowser.maybeCompleteAuthSession();

const APP_SCHEME = 'adhd-calendar';
const googleClientId = process.env.EXPO_PUBLIC_GOOGLE_CLIENT_ID || '';
const googleIosClientId = process.env.EXPO_PUBLIC_GOOGLE_IOS_CLIENT_ID || '';
const googleAndroidClientId = process.env.EXPO_PUBLIC_GOOGLE_ANDROID_CLIENT_ID || '';

export default function CalendarSettingsScreen() {
    const [loading, setLoading] = useState<string | null>(null);

    const [request, response, promptAsync] = Google.useAuthRequest({
        androidClientId: googleAndroidClientId,
        iosClientId: googleIosClientId,
        clientId: googleClientId,
        redirectUri: makeRedirectUri({
            scheme: APP_SCHEME,
            path: 'auth/google',
            preferLocalhost: __DEV__,
            native: `${APP_SCHEME}://auth/google`,
        }),
        scopes: [
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/calendar.events',
            'https://www.googleapis.com/auth/calendar.readonly',
        ],
    });

    const handleGoogleConnect = async () => {
        setLoading('google');
        try {
            const authResponse = await promptAsync({ showInRecents: true });

            if (authResponse?.type === 'success' && authResponse.authentication) {
                await calendarService.setGoogleToken(authResponse.authentication.accessToken);
                Toast.show({
                    type: 'success',
                    text1: 'Success',
                    text2: 'Connected to Google Calendar',
                });
            }
        } catch (error) {
            Toast.show({
                type: 'error',
                text1: 'Error',
                text2: 'Failed to connect to Google Calendar',
            });
        } finally {
            setLoading(null);
        }
    };

    const handleAppleConnect = async () => {
        setLoading('apple');
        try {
            const success = await calendarService.connectAppleCalendar();
            if (success) {
                Toast.show({
                    type: 'success',
                    text1: 'Success',
                    text2: 'Connected to Apple Calendar',
                });
            }
        } catch (error) {
            Toast.show({
                type: 'error',
                text1: 'Error',
                text2: 'Failed to connect to Apple Calendar',
            });
        } finally {
            setLoading(null);
        }
    };

    const handleOutlookConnect = async () => {
        setLoading('outlook');
        try {
            const success = await calendarService.connectOutlookCalendar();
            if (success) {
                Toast.show({
                    type: 'success',
                    text1: 'Success',
                    text2: 'Connected to Outlook Calendar',
                });
            }
        } catch (error) {
            Toast.show({
                type: 'error',
                text1: 'Error',
                text2: 'Failed to connect to Outlook Calendar',
            });
        } finally {
            setLoading(null);
        }
    };

    return (
        <View style={styles.container}>
            <Text h4 style={styles.title}>Calendar Settings</Text>

            <View style={styles.buttonContainer}>
                <AnimatedButton
                    title="Connect Google Calendar"
                    onPress={handleGoogleConnect}
                    loading={loading === 'google'}
                    disabled={loading !== null || !request}
                    containerStyle={styles.button}
                    icon={{
                        name: 'google',
                        type: 'font-awesome',
                        color: 'white',
                    }}
                    scaleOnPress
                />

                <AnimatedButton
                    title="Connect Apple Calendar"
                    onPress={handleAppleConnect}
                    loading={loading === 'apple'}
                    disabled={loading !== null}
                    containerStyle={styles.button}
                    icon={{
                        name: 'apple',
                        type: 'font-awesome',
                        color: 'white',
                    }}
                    scaleOnPress
                />

                <AnimatedButton
                    title="Connect Outlook Calendar"
                    onPress={handleOutlookConnect}
                    loading={loading === 'outlook'}
                    disabled={loading !== null}
                    containerStyle={styles.button}
                    icon={{
                        name: 'microsoft',
                        type: 'font-awesome-5',
                        color: 'white',
                    }}
                    scaleOnPress
                />
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        padding: 16,
        backgroundColor: '#fff',
    },
    title: {
        marginBottom: 24,
        textAlign: 'center',
    },
    buttonContainer: {
        gap: 16,
    },
    button: {
        marginVertical: 8,
        borderRadius: 8,
        overflow: 'hidden',
    },
});
