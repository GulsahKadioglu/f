"use client";

/**
 * @file frontend/src/app/fl-dashboard/page.tsx
 * @description This Next.js page provides a dashboard for Federated Learning (FL) metrics,
 * displaying accuracy and loss over training rounds using Chart.js. It also
 * includes functionality to manually start a new FL round.
 */

import React, { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { apiClient } from '@/services/api';
import { AxiosResponse, AxiosInstance } from 'axios';

const FLChart = dynamic(() => import('@/components/FLChart'), {
  ssr: false,
  loading: () => <p>Loading chart...</p>,
});

/**
 * Interface for a Federated Learning Round Metric object.
 * Defines the structure of the data expected for FL metrics.
 */
interface FLRoundMetric {
  id: number;
  round_number: number;
  avg_accuracy: number;
  avg_loss: number;
  num_clients: number;
  timestamp: string;
}

/**
 * FLDashboardPage component.
 *
 * This component fetches and displays federated learning round metrics in a line chart.
 * It also provides a button to initiate a new FL training round.
 *
 * @returns {JSX.Element} The Federated Learning Dashboard page.
 */
export default function FLDashboardPage() {
  const [metrics, setMetrics] = useState<FLRoundMetric[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [startFLRoundLoading, setStartFLRoundLoading] = useState<boolean>(false);
  const [startFLRoundError, setStartFLRoundError] = useState<string | null>(null);
  const [startFLRoundSuccess, setStartFLRoundSuccess] = useState<string | null>(null);

  /**
   * Fetches the federated learning metrics from the backend.
   *
   * Sets the loading state, makes an API call, and updates the `metrics` state.
   * Handles potential errors during the fetch operation.
   */
  const fetchMetrics = async () => {
    try {
      setLoading(true);
      const typedApiClient: AxiosInstance = apiClient;
      const response: AxiosResponse<FLRoundMetric[]> = await typedApiClient.get<FLRoundMetric[]>('/api/v1/reports/fl-metrics');
      setMetrics(response.data);
    } catch (err) {
      setError('An error occurred while loading FL metrics.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * useEffect hook to fetch FL metrics when the component mounts.
   */
  useEffect(() => {
    fetchMetrics();
  }, []);

  /**
   * Handles the initiation of a new Federated Learning round.
   *
   * Sets loading state, makes an API call to trigger a new FL round on the backend.
   * Updates success or error messages based on the API response and refetches metrics.
   */
  const handleStartFLRound = async () => {
    setStartFLRoundLoading(true);
    setStartFLRoundError(null);
    setStartFLRoundSuccess(null);
    try {
      const typedApiClient: AxiosInstance = apiClient;
      const response: AxiosResponse<any> = await typedApiClient.post('/api/v1/reports/start-fl-round');
      setStartFLRoundSuccess(response.data.message);
      // Fetch metrics again after a new round has started
      fetchMetrics();
    } catch (err) {
      setStartFLRoundError('An error occurred while starting the FL round.');
      console.error(err);
    } finally {
      setStartFLRoundLoading(false);
    }
  };

  // Display a loading message while metrics are being fetched.
  if (loading) {
    return (
      <main className="min-h-screen bg-gray-100 p-8 flex items-center justify-center">
        <p className="text-center text-gray-500 text-lg">Loading metrics...</p>
      </main>
    );
  }

  // Display an error message if fetching metrics failed.
  if (error) {
    return (
      <main className="min-h-screen bg-gray-100 p-8 flex items-center justify-center">
        <p className="text-center text-red-500 text-lg">Error: {error}</p>
      </main>
    );
  }

  // Prepare data for the Chart.js line chart.
  const chartData = {
    labels: metrics.map(m => `Round ${m.round_number}`),
    datasets: [
      {
        label: 'Average Accuracy',
        data: metrics.map(m => m.avg_accuracy),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
        tension: 0.1,
      },
      {
        label: 'Average Loss',
        data: metrics.map(m => m.avg_loss),
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
        tension: 0.1,
        yAxisID: 'y1', // Use a second Y-axis for loss
      },
      {
        label: 'Number of Clients',
        data: metrics.map(m => m.num_clients),
        borderColor: 'rgb(54, 162, 235)',
        backgroundColor: 'rgba(54, 162, 235, 0.5)',
        tension: 0.1,
        yAxisID: 'y2', // Use a third Y-axis for number of clients
      },
    ],
  };

  // Chart.js options for responsiveness, interaction, and scales.
  const chartOptions = {
    responsive: true,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    stacked: false,
    plugins: {
      title: {
        display: true,
        text: 'Federated Learning Metrics',
      },
    },
    scales: {
      y: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        title: {
          display: true,
          text: 'Accuracy',
        },
      },
      y1: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        grid: {
          drawOnChartArea: false,
        },
        title: {
          display: true,
          text: 'Loss',
        },
      },
      y2: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        grid: {
          drawOnChartArea: false,
        },
        title: {
          display: true,
          text: 'Number of Clients',
        },
      },
    },
  };

  return (
    <main className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-5xl mx-auto bg-white p-8 rounded-lg shadow-md">
        <h1 className="text-3xl font-bold text-gray-800 mb-6 text-center">FL Metrics Dashboard</h1>
        
        {/* Button to start a new FL round */}
        <div className="mb-6 text-center">
          <button
            onClick={handleStartFLRound}
            disabled={startFLRoundLoading}
            className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            {startFLRoundLoading ? 'Starting Round...' : 'Start FL Round'}
          </button>
          {startFLRoundError && <p className="text-red-500 text-sm mt-2">Error: {startFLRoundError}</p>}
          {startFLRoundSuccess && <p className="text-green-500 text-sm mt-2">{startFLRoundSuccess}</p>}
        </div>

        {/* Display chart or no metrics message */}
        {metrics.length === 0 ? (
          <p className="text-center text-gray-500">No FL metrics found yet.</p>
        ) : (
          <div className="relative h-96">
            <FLChart data={chartData} options={chartOptions} />
          </div>
        )}
      </div>
    </main>
  );
}