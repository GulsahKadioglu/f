"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/router';
import { apiClient } from '@/services/api';
import { motion, AnimatePresence } from 'framer-motion'; // Import motion and AnimatePresence
import Link from 'next/link';
import { AxiosResponse, AxiosInstance } from 'axios';
import { TextField, Button } from '@mui/material';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const typedApiClient: AxiosInstance = apiClient;
      const response: AxiosResponse<any> = await typedApiClient.post('/api/v1/auth/login', {
        email,
        password,
      });
      localStorage.setItem('access_token', response.data.access_token);
      router.push('/cases');
    } catch (err) {
      setError('Login failed. Please check your email and password.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md p-6">
        <div>
          <h1 className="text-3xl font-bold text-center mb-6">Login</h1>
          <div className="relative">
            {loading ? (
              <motion.div
                key="loading-indicator"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 bg-white dark:bg-gray-900 bg-opacity-70 dark:bg-opacity-70 flex items-center justify-center z-10 rounded-lg"
              >
                <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
              </motion.div>
            ) : null}
            <form onSubmit={handleLogin} className="space-y-6">
              <TextField
                required
                fullWidth
                label="Email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={loading}
                variant="outlined"
              />
              <TextField
                required
                fullWidth
                label="Password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loading}
                variant="outlined"
              />
              <div className="text-right">
                <Link href="/forgot-password" className="text-sm text-blue-600 hover:underline">
                  Forgot your password?
                </Link>
              </div>
              {error && <p className="text-red-500 text-sm text-center">{error}</p>}
              <Button
                type="submit"
                fullWidth
                variant="contained"
                color="primary"
                disabled={loading}
              >
                {loading ? 'Logging in...' : 'Login'}
              </Button>
            </form>
          </div>
          <p className="mt-6 text-center text-sm">
            Don&apos;t have an account?{' '}
            <Link href="/register">
              Register
            </Link>
          </p>
        </div>
      </div>
    </main>
  );
}
