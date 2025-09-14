/**
 * AppNavigator.tsx
 *
 * This file manages the main navigation flow of the mobile application.
 * It handles the authentication state, determining whether to display the
 * authentication screens (Login/Register) or the main application content (AppTabs).
 * It uses `@react-navigation/stack` for stack navigation and `react-native-keychain`
 * for secure storage of user tokens.
 *
 * Purpose:
 * - To define the root navigation structure of the application.
 * - To implement an authentication flow that checks for existing user sessions.
 * - To conditionally render different navigation stacks based on the user's authentication status.
 * - To provide a splash screen experience while checking authentication.
 *
 * Key Components:
 * - `NavigationContainer`: The top-level component for managing navigation state.
 * - `createStackNavigator`: Creates a stack navigator for screen transitions.
 * - `react-native-keychain`: Securely stores and retrieves user credentials.
 * - `LoginScreen`, `RegisterScreen`, `AppTabs`, `SplashScreen`: Imported components
 *   representing different parts of the application's UI.
 */

import React, { useState, useEffect } from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createStackNavigator } from "@react-navigation/stack";
import * as Keychain from "react-native-keychain";

import LoginScreen from "../screens/LoginScreen";
import RegisterScreen from "../screens/RegisterScreen";
import AppTabs from "./AppTabs";
import SplashScreen from "../screens/SplashScreen";
import OnboardingScreen from "../screens/OnboardingScreen";
import AsyncStorage from "@react-native-async-storage/async-storage";

const Stack = createStackNavigator();

/**
 * AppNavigator component.
 *
 * This component is responsible for the overall navigation of the application.
 * It checks for an existing user token in the Keychain to determine if the user
 * is already logged in. Based on the authentication status, it renders either
 * the authentication flow (Login/Register) or the main application tabs.
 *
 * @returns {JSX.Element} The navigation container with the appropriate stack navigator.
 */
const AppNavigator = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [userToken, setUserToken] = useState<string | null>(null);
  const [hasViewedOnboarding, setHasViewedOnboarding] = useState<boolean | null>(null);

  useEffect(() => {
    const checkAppStatus = async () => {
      try {
        // Check onboarding status
        const onboarded = await AsyncStorage.getItem('hasViewedOnboarding');
        setHasViewedOnboarding(onboarded === 'true');

        // Check user token
        const credentials = await Keychain.getGenericPassword();
        if (credentials) {
          setUserToken(credentials.password);
        }
      } catch (error) {
        console.log("Error checking app status:", error);
      } finally {
        setIsLoading(false);
      }
    };

    checkAppStatus();
  }, []);

  // Show a splash screen while checking the authentication status
  if (isLoading) {
    return <SplashScreen />;
  }

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {hasViewedOnboarding === false ? (
          <Stack.Screen name="Onboarding" component={OnboardingScreen} />
        ) : userToken == null ? (
          <>
            <Stack.Screen name="Login" component={LoginScreen} />
            <Stack.Screen name="Register" component={RegisterScreen} />
          </>
        ) : (
          <Stack.Screen name="App" component={AppTabs} />
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default AppNavigator;
