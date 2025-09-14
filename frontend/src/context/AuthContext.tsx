"use client";

/**
 * @file frontend/src/context/AuthContext.tsx
 * @description This file defines the authentication context for the Next.js application.
 * It provides authentication state, login/logout functions, and handles redirection
 * based on the user's authentication status.
 */

import React, { createContext, useState, useEffect, useContext } from 'react';
import { useRouter } from 'next/router';
import { apiClient } from '@/services/api';

/**
 * Interface for the AuthContextType.
 * Defines the shape of the authentication context.
 */
interface AuthContextType {
  isAuthenticated: boolean;
  login: (token: string) => void;
  logout: () => void;
  loading: boolean;
}

// Create the AuthContext with an undefined initial value.
const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * AuthProvider component.
 *
 * This component provides the authentication context to its children.
 * It manages the `isAuthenticated` state, handles token storage in local storage,
 * and redirects users to the login page if they are not authenticated and
 * trying to access protected routes.
 *
 * @param {object} props - Component props.
 * @param {React.ReactNode} props.children - The child components to be wrapped by the provider.
 * @returns {JSX.Element} The AuthProvider component.
 */
export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const router = useRouter();
  const pathname = router.asPath;

  

  /**
   * useEffect hook to check authentication status on component mount.
   *
   * It checks for an existing access token in local storage to determine
   * if the user is already authenticated.
   */
  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        setIsAuthenticated(true);
      } else {
        setIsAuthenticated(false);
      }
      setLoading(false);
    };
    checkAuth();
  }, []);

  /**
   * useEffect hook to handle redirection based on authentication status.
   *
   * If the user is not authenticated and tries to access a protected route
   * (not login or register page), they are redirected to the login page.
   */
  useEffect(() => {
    if (!loading) {
      // Check authentication for all pages except login and register
      if (!isAuthenticated && pathname !== '/login' && pathname !== '/register') {
        router.push('/login');
      }
    }
  }, [isAuthenticated, loading, pathname, router]);

  /**
   * Logs in the user by storing the access token and updating authentication state.
   *
   * @param {string} token - The access token received upon successful login.
   */
  const login = (token: string) => {
    localStorage.setItem('access_token', token);
    setIsAuthenticated(true);
  };

  /**
   * Logs out the user by removing the access token and updating authentication state.
   *
   * Redirects the user to the login page after logout.
   */
  const logout = () => {
    localStorage.removeItem('access_token');
    setIsAuthenticated(false);
    router.push('/login');
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

/**
 * Custom hook to consume the authentication context.
 *
 * Throws an error if used outside of an `AuthProvider`.
 *
 * @returns {AuthContextType} The authentication context values.
 * @throws {Error} If `useAuth` is not used within an `AuthProvider`.
 */
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};