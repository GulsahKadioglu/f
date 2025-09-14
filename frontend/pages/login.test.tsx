import React from 'react';
import { render, screen } from '@testing-library/react';
import LoginPage from './login';

// Mock the useRouter hook
jest.mock('next/router', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

describe('LoginPage', () => {
  it('renders the login form', () => {
    render(<LoginPage />);

    // Check if the main heading is there
    expect(screen.getByRole('heading', { name: /login/i })).toBeInTheDocument();

    // Check for email and password inputs
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();

    // Check for the login button
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });
});
