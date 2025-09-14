/**
 * SplashScreen.tsx
 *
 * This screen displays a simple splash screen with a loading indicator.
 * It is typically shown while the application is initializing or performing
 * background tasks, such as checking user authentication status or loading initial data.
 *
 * Purpose:
 * - To provide immediate visual feedback to the user upon app launch.
 * - To mask any initial loading times or asynchronous operations.
 * - To create a smooth user experience by preventing a blank screen during startup.
 *
 * Key Components:
 * - `ActivityIndicator`: A UI component from React Native that displays a circular loading indicator.
 * - `StyleSheet`: For defining the visual styles of the component.
 *
 * Usage:
 * - This component is usually rendered conditionally at the root of the application
 *   while initial setup or authentication checks are in progress.
 */

import React from "react";
import { View, ActivityIndicator, StyleSheet } from "react-native";

/**
 * SplashScreen component.
 *
 * A simple component that displays a full-screen loading indicator.
 * It's used to provide visual feedback to the user while the app is
 * loading or performing initial setup.
 *
 * @returns {JSX.Element} The Splash screen.
 */
const SplashScreen = () => {
  return (
    <View style={styles.container}>
      <ActivityIndicator size="large" />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
});

export default SplashScreen;
