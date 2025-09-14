import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import CasesList from './CasesList';
import { apiClient } from '@/services/api';

// Mock the apiClient to control its behavior in tests
jest.mock('@/services/api', () => ({
  apiClient: {
    get: jest.fn(),
  },
}));

// Mock the useRouter hook
jest.mock('next/router', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

// A helper to cast the mocked apiClient
const mockedApiClient = apiClient as jest.Mocked<typeof apiClient>;

describe('CasesList', () => {
  // Reset mocks before each test
  beforeEach(() => {
    mockedApiClient.get.mockClear();
  });

  it('shows a loading message initially', () => {
    mockedApiClient.get.mockResolvedValue({ data: [] });
    render(<CasesList />);
    // The "Loading..." message should be present on the initial render
    expect(screen.getByText(/Loading cases.../i)).toBeInTheDocument();
  });

  it('shows an error message if data fetching fails', async () => {
    const errorMessage = 'API Error';
    mockedApiClient.get.mockRejectedValue(new Error(errorMessage));
    render(<CasesList />);

    // Use waitFor to handle state updates gracefully
    await waitFor(() => {
      expect(screen.getByText(/An error occurred while loading cases./i)).toBeInTheDocument();
    });
  });

  it('displays a table of cases when data is fetched successfully', async () => {
    const mockCases = [
      { id: 1, patient_id: 'P001', case_date: '2023-01-01T12:00:00Z', status: 'Active' },
      { id: 2, patient_id: 'P002', case_date: '2023-01-02T12:00:00Z', status: 'Pending' },
    ];
    mockedApiClient.get.mockResolvedValue({ data: mockCases });

    render(<CasesList />);

    // Use waitFor to ensure all assertions related to the async update are checked together
    await waitFor(() => {
      expect(screen.getByText('P001')).toBeInTheDocument();
      expect(screen.getByText('P002')).toBeInTheDocument();
    });

    // The loading message should disappear after the update
    expect(screen.queryByText(/Loading cases.../i)).not.toBeInTheDocument();
  });
});
