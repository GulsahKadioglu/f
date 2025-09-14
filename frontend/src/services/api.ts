/**
 * @file frontend/src/services/api.ts
 * @description Configures and exports an Axios instance for making API requests
 * to the backend. It includes an interceptor to automatically attach the
 * authentication token from local storage to every outgoing request.
 */

import axios from 'axios';

// Base URL for the backend API, loaded from environment variables or defaults to localhost.
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000';

/**
 * Axios API client instance.
 *
 * Configured with the base URL and default headers for JSON content.
 */
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request interceptor to attach authentication token.
 *
 * This interceptor runs before each request. It attempts to retrieve the
 * access token from local storage and adds it to the `Authorization`
 * header as a Bearer token. This ensures that authenticated requests are
 * automatically handled.
 */
if (typeof window !== 'undefined') {
  apiClient.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );
}

export default apiClient;