/**
 * App.tsx
 *
 * This file serves as the main entry point for the React Native mobile application.
 * It sets up the primary navigation structure using `@react-navigation/native`
 * and handles the crucial process of registering the device for push notifications
 * using Expo's Notifications API.
 *
 * Purpose:
 * - To initialize the root component of the application.
 * - To configure the global notification handler for incoming push notifications.
 * - To manage the lifecycle of push notification token registration with the backend.
 * - To integrate the main navigation flow of the application.
 *
 * Key Components:
 * - `NavigationContainer`: Manages the navigation tree and contains the navigation state.
 * - `AppNavigator`: Defines the stack of screens and their navigation flow.
 * - `expo-notifications`: Library for handling push notifications.
 * - `expo-constants`: Provides access to the Expo app's configuration.
 * - `apiClient`: Custom service for making API calls to the backend.
 *
 * Note:
 * - This file is critical for the application's startup and core functionalities.
 * - Push notification registration is performed on app launch to ensure the device
 *   can receive notifications from the server.
 */

import "react-native-gesture-handler";
import React, { useEffect } from "react";
import { NavigationContainer } from "@react-navigation/native";
import AppNavigator from "./src/navigation/AppNavigator";
import * as Notifications from "expo-notifications";
import Constants from "expo-constants";
import { Platform } from "react-native";
import apiClient from "./src/services/api";

// Sets the global notification handler for how notifications should be presented when the app is in the foreground.
// This configuration ensures that notifications will show an alert, but will not play a sound or set a badge.
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: false,
    shouldSetBadge: false,
  }),
});

/**
 * The main component of the mobile application.
 *
 * This component sets up the navigation container and handles the registration
 * for push notifications.
 *
 * @returns {JSX.Element} The root component of the application.
 */
const App = () => {
  useEffect(() => {
    registerForPushNotificationsAsync();
  }, []);

  /**
   * Registers the device for push notifications.
   *
   * This asynchronous function performs the following steps:
   * 1. Checks if the code is running on a physical device (required for push notifications).
   * 2. Requests notification permissions from the user if they haven't been granted yet.
   * 3. Retrieves the Expo push token for the device.
   * 4. Sends this token to the backend API to associate it with the user's account,
   *    enabling the backend to send targeted push notifications.
   * 5. Configures a notification channel for Android devices (required for Android 8.0+).
   *
   * @returns {Promise<string | undefined>} A Promise that resolves with the Expo push token
   *                                       if registration is successful, or `undefined` if it fails.
   */
  async function registerForPushNotificationsAsync() {
    let token;
    if (Constants.isDevice) {
      const { status: existingStatus } =
        await Notifications.getPermissionsAsync();
      let finalStatus = existingStatus;
      if (existingStatus !== "granted") {
        const { status } = await Notifications.requestPermissionsAsync();
        finalStatus = status;
      }
      if (finalStatus !== "granted") {
        alert("Failed to get push token for push notification!");
        return;
      }
      token = (await Notifications.getExpoPushTokenAsync()).data;
      console.log(token);
      try {
        await apiClient.post("/api/v1/users/register-push-token", { token });
        console.log("Push token successfully registered with backend.");
      } catch (error) {
        console.error("Failed to register push token with backend:", error);
      }
    } else {
      alert("Must use physical device for Push Notifications");
    }

    if (Platform.OS === "android") {
      Notifications.setNotificationChannelAsync("default", {
        name: "default",
        importance: Notifications.AndroidImportance.DEFAULT,
        vibrationPattern: [0, 250, 250, 250],
        lightColor: "#FF231F7C",
      });
    }

    return token;
  }

  return (
    <NavigationContainer>
      <AppNavigator />
    </NavigationContainer>
  );
};

export default App;