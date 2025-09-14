/**
 * LoginScreen.tsx
 *
 * This screen provides the user interface for logging into the mobile application.
 * It handles user input for email and password, sends these credentials to the
 * backend API for authentication, and securely stores the received access token
 * upon successful login. It then navigates the user to the main application content.
 *
 * Purpose:
 * - To allow existing users to authenticate and gain access to the application.
 * - To securely handle user credentials and access tokens.
 * - To provide clear feedback to the user regarding login status (loading, error).
 * - To facilitate navigation to the registration screen for new users.
 *
 * Key Components:
 * - `useState`: React hook for managing component state (email, password, loading, error).
 * - `TextInput`, `Button`, `Text`: UI components from `react-native-paper` for form input and actions.
 * - `apiClient`: Custom service for making authenticated API calls to the backend.
 * - `react-native-keychain`: For securely storing the user's access token.
 *
 * Data Flow:
 * - User enters `email` and `password`.
 * - `handleLogin` sends a POST request to `/api/v1/auth/login`.
 * - On success, `access_token` is stored in Keychain, and navigation to 'App' occurs.
 * - On failure, an error message is displayed.
 */

import React, { useState } from "react";
import { View, StyleSheet } from "react-native";
import { TextInput, Button, Text } from "react-native-paper";
import apiClient from "../services/api";
import * as Keychain from "react-native-keychain";

/**
 * LoginScreen component.
 *
 * Allows users to log in with their email and password. Upon successful
 * authentication, it stores the access token securely using Keychain
 * and navigates the user to the main application.
 *
 * @param {object} props - Component props.
 * @param {object} props.navigation - The navigation object from React Navigation.
 * @returns {JSX.Element} The Login screen.
 */
const LoginScreen = ({ navigation }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  /**
   * Handles the login process.
   *
   * This asynchronous function performs the following steps:
   * 1. Sets loading state to `true` and clears any previous error messages.
   * 2. Sends a POST request to the backend's login endpoint (`/api/v1/auth/login`)
   *    with the user's email and password.
   * 3. If the request is successful, it extracts the `access_token` from the response.
   * 4. Securely stores the `access_token` in the device's Keychain, associated with the user's email.
   * 5. Navigates the user to the main application (`App` navigator).
   * 6. If an error occurs during the process (e.g., network error, invalid credentials),
   *    it sets an appropriate error message and logs the detailed error.
   * 7. Finally, it sets loading state to `false`.
   */
  const handleLogin = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await apiClient.post("/api/v1/auth/login", {
        email,
        password,
      });

      const { access_token } = response.data;
      await Keychain.setGenericPassword(email, access_token);
      navigation.navigate("App");
    } catch (e) {
      setError("Login failed. Please check your email and password.");
      console.error("Login error:", e.response?.data || e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <TextInput
        label="Email"
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
        autoCapitalize="none"
        style={styles.input}
        mode="outlined"
      />
      <TextInput
        label="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
        style={styles.input}
        mode="outlined"
      />
      {error ? <Text style={styles.error}>{error}</Text> : null}
      <Button
        mode="contained"
        onPress={handleLogin}
        loading={loading}
        style={styles.button}
      >
        Login
      </Button>
      <Button
        onPress={() => navigation.navigate("Register")}
        style={styles.button}
      >
        Register
      </Button>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    padding: 16,
    backgroundColor: "#f5f5f5",
  },
  input: {
    marginBottom: 15,
  },
  button: {
    marginTop: 10,
  },
  error: {
    color: "red",
    marginBottom: 10,
    textAlign: "center",
  },
});

export default LoginScreen;
