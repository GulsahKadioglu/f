"use client";

/**
 * @file frontend/src/app/model-versions/page.tsx
 * @description This Next.js page displays a list of federated learning model versions.
 * It fetches model version details from the backend API and presents them in a table.
 */

import React, { useEffect, useState } from 'react';
import { apiClient } from '@/services/api';
import Link from 'next/link';
import { AxiosResponse, AxiosInstance } from 'axios';

/**
 * Interface for a Model Version object.
 * Defines the structure of the data expected for a model version.
 */
interface ModelVersion {
  id: string;
  version_number: number;
  created_at: string;
  avg_accuracy: number;
  avg_loss: number;
  description: string;
  file_path: string;
}

/**
 * ModelVersionsPage component.
 *
 * This component fetches and displays a list of federated learning model versions
 * in a tabular format. It shows key metrics and provides links to view more details
 * for each model version.
 *
 * @returns {JSX.Element} The Model Versions management page.
 */
export default function ModelVersionsPage() {
  const [modelVersions, setModelVersions] = useState<ModelVersion[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  /**
   * useEffect hook to fetch model versions when the component mounts.
   *
   * It makes an API call to retrieve the model versions and updates the
   * `modelVersions` state. Handles loading state and potential errors.
   */
  useEffect(() => {
    const fetchModelVersions = async () => {
      try {
        setLoading(true);
        const typedApiClient: AxiosInstance = apiClient;
        const response: AxiosResponse<ModelVersion[]> = await typedApiClient.get<ModelVersion[]>('/api/v1/model-versions/');
        setModelVersions(response.data);
      } catch (err) {
        setError('An error occurred while loading model versions.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchModelVersions();
  }, []);

  // Display a loading message while model versions are being fetched.
  if (loading) {
    return (
      <main className="min-h-screen bg-gray-100 p-8 flex items-center justify-center">
        <p className="text-center text-gray-500 text-lg">Loading model versions...</p>
      </main>
    );
  }

  // Display an error message if fetching model versions failed.
  if (error) {
    return (
      <main className="min-h-screen bg-gray-100 p-8 flex items-center justify-center">
        <p className="text-center text-red-500 text-lg">Error: {error}</p>
      </main>
    );
  }

  // Display a message if no saved model versions are found.
  if (modelVersions.length === 0) {
    return (
      <main className="min-h-screen bg-gray-100 p-8 flex items-center justify-center">
        <p className="text-center text-gray-500 text-lg">No saved model versions found yet.</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-7xl mx-auto bg-white p-8 rounded-lg shadow-md">
        <h1 className="text-3xl font-bold text-gray-800 mb-6 text-center">Model Versions Management</h1>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Version No</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Creation Date</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Accuracy</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Loss</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {modelVersions.map((version) => (
                <tr key={version.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{version.version_number}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{new Date(version.created_at).toLocaleDateString()}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{(version.avg_accuracy * 100).toFixed(2)}%</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{version.avg_loss.toFixed(4)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{version.description}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <Link href={`/model-versions/${version.id}`} className="text-blue-600 hover:text-blue-900">
                      Details
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </main>
  );
}