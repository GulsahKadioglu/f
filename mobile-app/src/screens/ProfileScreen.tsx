/**
 * ProfileScreen.tsx
 *
 * This screen displays the authenticated user's profile information and provides
 * functionalities related to user management and push notifications. It allows
 * users to view their details, log out, send test notifications, and register
 * their device for push notifications with the backend.
 *
 * Purpose:
 * - To present the current user's profile data (email, active status, admin status).
 * - To enable secure logout from the application.
 * - To provide testing utilities for push notifications.
 * - To facilitate the registration of device push tokens with the backend for targeted notifications.
 *
 * Key Components:
 * - `useState`, `useEffect`: React hooks for managing component state and side effects.
 * - `react-native-paper`: UI components (Card, Title, Paragraph, Button, Text, ActivityIndicator).
 * - `react-native-keychain`: For securely managing user authentication tokens.
 * - `expo-notifications`: For handling push notification permissions and token retrieval.
 * - `apiClient`: Custom service for making authenticated API calls to the backend.
 *
 * Data Flow:
 * - `useEffect` fetches user profile from `/api/v1/users/me` on component mount.
 * - `handleLogout` clears credentials and navigates to LoginScreen.
 * - `sendTestNotification` schedules a local Expo notification.
 * - `registerPushToken` requests permissions, gets Expo token, and sends it to backend.
 */

import React, { useState, useEffect } from "react";
import { View, StyleSheet, ActivityIndicator, Alert } from "react-native";
import { Card, Title, Button, Text } from "react-native-paper";
import * as Keychain from "react-native-keychain";
import * as Notifications from "expo-notifications";
import apiClient from "../services/api";

interface UserProfile {
  email: string;
  is_active: boolean;
  is_admin: boolean;
}

/**
 * ProfileScreen component.
 *
 * Displays the authenticated user's profile details, such as email, account status,
 * and admin status. It also provides functionality to log out, send a test
 * push notification, and register the device's push token with the backend.
 *
 * @param {object} props - Component props.
 * @param {object} props.navigation - The navigation object from React Navigation.
 * @returns {JSX.Element} The Profile screen.
 */
const ProfileScreen = ({ navigation }) => {
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true);
        const response = await apiClient.get("/api/v1/users/me");
        setUserProfile(response.data);
        setError(null);
      } catch (err) {
        setError("An error occurred while loading profile information.");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  /**
   * Handles the user logout process.
   *
   * Prompts the user for confirmation, then clears the stored credentials
   * from Keychain and navigates back to the Login screen.
   */
  const handleLogout = async () => {
    Alert.alert(
      "Logout",
      "Are you sure you want to log out from your account?",
      [
        { text: "Cancel", style: "cancel" },
        {
          text: "Yes",
          onPress: async () => {
            await Keychain.resetGenericPassword();
            navigation.navigate("Login");
          },
        },
      ],
      { cancelable: false },
    );
  };

  /**
   * Sends a test push notification to the device.
   *
   * This function schedules a local notification immediately for testing purposes.
   */
  const sendTestNotification = async () => {
    await Notifications.scheduleNotificationAsync({
      content: {
        title: "Test Notification!",
        body: "This is a test notification.",
      },
      trigger: null,
    });
  };

  /**
   * Registers the device's push notification token with the backend.
   *
   * It requests notification permissions, retrieves the Expo push token,
   * and then sends it to the backend API to associate it with the user's profile.
   */
  const registerPushToken = async () => {
    try {
      const { status: existingStatus } =
        await Notifications.getPermissionsAsync();
      let finalStatus = existingStatus;
      if (existingStatus !== "granted") {
        const { status } = await Notifications.requestPermissionsAsync();
        finalStatus = status;
      }
      if (finalStatus !== "granted") {
        Alert.alert(
          "Permission Required",
          "Push notification permission not granted!",
        );
        return;
      }
      const token = (await Notifications.getExpoPushTokenAsync()).data;
      console.log("Expo Push Token:", token);
      await apiClient.post("/api/v1/users/register-push-token", { token });
      Alert.alert(
        "Success",
        "Notification token received and ready to be saved.",
      );
    } catch (e) {
      console.error("Error getting notification token:", e);
      Alert.alert(
        "Error",
        "An issue occurred while getting the notification token.",
      );
    }
  };

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator animating={true} size="large" />
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.centered}>
        <Text style={styles.errorText}>{error}</Text>
      </View>
    );
  }

  if (!userProfile) {
    return (
      <View style={styles.centered}>
        <Text style={styles.errorText}>Profile not found.</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <Title style={styles.title}>User Profile</Title>

          <View style={styles.detailRow}>
            <Text style={styles.label}>Email:</Text>
            <Text style={styles.value}>{userProfile.email}</Text>
          </View>

          <View style={styles.detailRow}>
            <Text style={styles.label}>Account Status:</Text>
            <Text style={styles.value}>
              {userProfile.is_active ? "Active" : "Inactive"}
            </Text>
          </View>

          <View style={styles.detailRow}>
            <Text style={styles.label}>Admin Status:</Text>
            <Text style={styles.value}>
              {userProfile.is_admin ? "Admin" : "User"}
            </Text>
          </View>
        </Card.Content>
      </Card>

      <Button
        mode="contained"
        onPress={sendTestNotification}
        style={styles.testNotificationButton}
      >
        Send Test Notification
      </Button>

      <Button
        mode="contained"
        onPress={registerPushToken}
        style={styles.registerTokenButton}
      >
        Register Notification Token
      </Button>

      <Button
        mode="contained"
        onPress={handleLogout}
        style={styles.logoutButton}
      >
        Logout
      </Button>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: "#f5f5f5",
  },
  centered: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  errorText: {
    color: "red",
    fontSize: 16,
  },
  card: {
    marginVertical: 8,
    borderRadius: 12,
    elevation: 4,
  },
  title: {
    fontSize: 22,
    fontWeight: "bold",
    marginBottom: 15,
    color: "#333",
  },
  detailRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 10,
    paddingBottom: 5,
    borderBottomWidth: 1,
    borderBottomColor: "#eee",
  },
  label: {
    fontSize: 16,
    fontWeight: "600",
    color: "#555",
  },
  value: {
    fontSize: 16,
    color: "#333",
  },
  logoutButton: {
    marginTop: 20,
    backgroundColor: "#dc3545",
  },
  testNotificationButton: {
    marginTop: 20,
    backgroundColor: "#28a745",
  },
  registerTokenButton: {
    marginTop: 10,
    backgroundColor: "#007bff",
  },
});

export default ProfileScreen;
