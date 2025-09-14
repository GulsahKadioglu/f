/**
 * RegisterScreen.tsx
 *
 * This screen provides the user interface for registering a new account in the
 * mobile application. It handles user input for email and password, sends these
 * credentials to the backend API for account creation, and provides feedback
 * to the user regarding the registration status.
 *
 * Purpose:
 * - To allow new users to create an account within the application.
 * - To securely collect and transmit new user credentials to the backend.
 * - To provide clear feedback to the user regarding registration status (loading, error).
 * - To facilitate navigation back to the login screen after successful registration.
 *
 * Key Components:
 * - `useState`: React hook for managing component state (email, password, loading, error).
 * - `TextInput`, `Button`, `Text`: UI components from `react-native-paper` for form input and actions.
 * - `apiClient`: Custom service for making authenticated API calls to the backend.
 *
 * Data Flow:
 * - User enters `email` and `password`.
 * - `handleRegister` sends a POST request to `/api/v1/auth/register`.
 * - On success, an alert is shown, and navigation to 'Login' occurs.
 * - On failure, an error message is displayed.
 */

import React, { useState } from "react";
import { View, StyleSheet, Alert } from "react-native";
import { TextInput, Button, Text } from "react-native-paper";
import apiClient from "../services/api";

/**
 * RegisterScreen component.
 *
 * Allows new users to register an account with their email and password.
 * Upon successful registration, it navigates the user to the Login screen.
 * Displays an error message if registration fails.
 *
 * @param {object} props - Component props.
 * @param {object} props.navigation - The navigation object from React Navigation.
 * @returns {JSX.Element} The Register screen.
 */
const RegisterScreen = ({ navigation }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  /**
   * Handles the registration process.
   *
   * This asynchronous function performs the following steps:
   * 1. Sets loading state to `true` and clears any previous error messages.
   * 2. Sends a POST request to the backend's registration endpoint (`/api/v1/auth/register`)
   *    with the new user's email and password.
   * 3. If the request is successful, it displays a success alert to the user.
   * 4. Navigates the user to the Login screen, prompting them to log in with their new credentials.
   * 5. If an error occurs during the process (e.g., network error, email already registered),
   *    it sets an appropriate error message and logs the detailed error.
   * 6. Finally, it sets loading state to `false`.
   */
  const handleRegister = async () => {
    setLoading(true);
    setError("");
    try {
      await apiClient.post("/api/v1/auth/register", { email, password });
      Alert.alert("Success", "Registration successful! Please log in.");
      navigation.navigate("Login");
    } catch (e) {
      setError("Registration failed. Please check your information.");
      console.error("Registration error:", e.response?.data || e.message);
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
        onPress={handleRegister}
        loading={loading}
        style={styles.button}
      >
        Register
      </Button>
      <Button
        onPress={() => navigation.navigate("Login")}
        style={styles.button}
      >
        Login
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

export default RegisterScreen;
