import React from "react";

import { Text, Button } from "@rneui/themed";
import { View, StyleSheet, ActivityIndicator } from "react-native";

import GamificationDashboard from "@/app/components/gamification/components/GamificationDashboard";
import { useGamification } from "@/contexts/GamificationContxt";

const GamificationScreen: React.FC = () => {
    const { loading, error, fetchGamificationData } = useGamification();

    const handleRefresh = async () => {
        try {
            await fetchGamificationData();
        } catch (error) {
            // Error handling is done in the context
        }
    };

    if (loading) {
        return (
            <View style={styles.centeredContainer}>
                <ActivityIndicator size="large" color="#007aff" />
                <Text style={styles.loadingText}>Loading Gamification Data...</Text>
            </View>
        );
    }

    return (
        <View style={styles.container}>
            <GamificationDashboard />
            <Button
                title="Refresh Gamification Data"
                onPress={handleRefresh}
                buttonStyle={styles.button}
                containerStyle={styles.buttonContainer}
            />
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: "#f9f9f9",
        paddingHorizontal: 15,
        paddingVertical: 10,
    },
    centeredContainer: {
        flex: 1,
        justifyContent: "center",
        alignItems: "center",
        backgroundColor: "#f9f9f9",
    },
    loadingText: {
        marginTop: 10,
        fontSize: 16,
        color: "#666",
    },
    buttonContainer: {
        marginVertical: 20,
    },
    button: {
        borderRadius: 8,
        paddingVertical: 10,
    },
});

export default GamificationScreen;
