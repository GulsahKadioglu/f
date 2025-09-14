/**
 * api.ts
 *
 * This file configures and exports an Axios instance for making HTTP requests
 * to the backend API from the mobile application. It includes a request interceptor
 * that automatically attaches the authentication token (retrieved from Keychain)
 * to every outgoing request, simplifying authenticated API calls.
 *
 * Purpose:
 * - To centralize API request configuration (base URL, headers).
 * - To automate the process of including authentication tokens in requests.
 * - To provide a consistent and easy-to-use client for interacting with the backend.
 *
 * Key Components:
 * - `axios`: The HTTP client library used for making requests.
 * - `react-native-keychain`: For securely storing and retrieving authentication tokens.
 * - `API_URL`: The base URL of the backend API, loaded from environment variables.
 * - `apiClient`: The configured Axios instance with default settings and interceptors.
 * - Request Interceptor: A middleware that modifies outgoing requests, specifically
 *   adding the `Authorization` header with the Bearer token.
 */

import axios from "axios";
import * as Keychain from "react-native-keychain";
import { API_URL } from "@env"; // Import API_URL from environment variables

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * Request interceptor to attach the authentication token.
 *
 * This interceptor is executed before every HTTP request made using `apiClient`.
 * It asynchronously retrieves the access token from `react-native-keychain`.
 * If a token is found, it is added to the `Authorization` header in the format
 * `Bearer <token>`. This ensures that all subsequent API calls are authenticated
 * without needing to manually add the token to each request.
 *
 * @param {object} config - The Axios request configuration object.
 * @returns {Promise<object>} A Promise that resolves with the modified configuration object.
 * @throws {Promise<Error>} A Promise that rejects with an error if token retrieval fails.
 */
apiClient.interceptors.request.use(
  async (config) => {
    try {
      const credentials = await Keychain.getGenericPassword();
      if (credentials) {
        config.headers.Authorization = `Bearer ${credentials.password}`;
      }
    } catch (error) {
      console.error("Failed to retrieve token from Keychain:", error);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

export default apiClient;
