"use client";

/**
 * @file frontend/src/components/ReportsList.tsx
 * @description This component displays a sortable and filterable list of analysis reports.
 * It fetches report data from the backend API and provides options to view report details.
 */

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { apiClient } from '@/services/api';
import { AxiosResponse, AxiosInstance } from 'axios';

/**
 * Interface for a Report object.
 * Defines the structure of the data expected for an analysis report.
 */
interface Report {
  id: number;
  created_at: string;
  avg_accuracy: number;
  avg_loss: number;
  num_clients: number;
}

/**
 * ReportsList component.
 *
 * Fetches and displays a list of analysis reports. Provides sorting and filtering
 * options for the reports. Each report is displayed with basic metrics and a
 * link to its detailed view.
 *
 * @returns {JSX.Element} The Reports List component.
 */
const ReportsList = () => {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<string>('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [minAccuracy, setMinAccuracy] = useState<string>('');

  /**
   * useEffect hook to fetch reports when sorting, ordering, or filtering parameters change.
   *
   * Constructs the API URL with query parameters for sorting and filtering,
   * then fetches the report data and updates the `reports` state.
   * Handles loading state and potential errors.
   */
  useEffect(() => {
    const fetchReports = async () => {
      try {
        setLoading(true);
        let url = '/api/v1/reports/';
        const params = new URLSearchParams();

        // Add sorting parameters
        params.append('sort_by', sortBy);
        params.append('sort_order', sortOrder);

        // Add filtering parameters
        if (minAccuracy) {
          params.append('min_accuracy', minAccuracy);
        }

        if (params.toString()) {
          url += `?${params.toString()}`;
        }

        const typedApiClient: AxiosInstance = apiClient;
        const response: AxiosResponse<Report[]> = await typedApiClient.get<Report[]>(url);
        setReports(response.data);
      } catch (err) {
        setError('An error occurred while loading reports.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchReports();
  }, [sortBy, sortOrder, minAccuracy]);

  // Display a loading message while reports are being fetched.
  if (loading) {
    return <p className="text-center text-gray-500">Loading reports...</p>;
  }

  // Display an error message if fetching reports failed.
  if (error) {
    return <p className="text-center text-red-500">Error: {error}</p>;
  }

  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
      {/* Sorting and Filtering Controls */}
      <div className="flex flex-col sm:flex-row justify-between items-center gap-4 mb-6 pb-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-4">
          <label htmlFor="sortBy" className="text-sm font-medium text-gray-600 dark:text-gray-300">Sort By:</label>
          <select
            id="sortBy"
            className="block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:focus:border-blue-400"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value="created_at">Creation Date</option>
            <option value="avg_accuracy">Accuracy</option>
            <option value="avg_loss">Loss</option>
            <option value="id">ID</option>
          </select>
        </div>
        <div className="flex items-center gap-4">
          <label htmlFor="sortOrder" className="text-sm font-medium text-gray-600 dark:text-gray-300">Order:</label>
          <select
            id="sortOrder"
            className="block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:focus:border-blue-400"
            value={sortOrder}
            onChange={(e) => setSortOrder(e.target.value as 'asc' | 'desc')}
          >
            <option value="desc">Descending</option>
            <option value="asc">Ascending</option>
          </select>
        </div>
        <div className="flex items-center gap-4">
          <label htmlFor="minAccuracy" className="text-sm font-medium text-gray-600 dark:text-gray-300">Min. Accuracy:</label>
          <input
            type="number"
            id="minAccuracy"
            className="block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:focus:border-blue-400"
            value={minAccuracy}
            onChange={(e) => setMinAccuracy(e.target.value)}
            placeholder="e.g.: 0.8"
            step="0.01"
            min="0"
            max="1"
          />
        </div>
      </div>

      {/* Reports List or Empty Message */}
      {reports.length === 0 ? (
        <div className="text-center py-10 text-gray-500 dark:text-gray-400">
          <p>No reports found matching the criteria.</p>
        </div>
      ) : (
        <ul role="list" className="divide-y divide-gray-200 dark:divide-gray-700">
          {reports.map((report) => (
            <li key={report.id} className="py-4 px-2 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-150 rounded-lg">
              <div className="flex items-center space-x-4">
                <div className="flex-shrink-0">
                  <span className={`h-10 w-10 rounded-full flex items-center justify-center text-white text-lg font-semibold ${report.avg_accuracy > 0.7 ? 'bg-green-500' : 'bg-yellow-500'}`}>
                    {`#${report.id}`}
                  </span>
                </div>
                <div className="min-w-0 flex-1 grid grid-cols-2 sm:grid-cols-4 gap-x-4 items-center">
                  <p className="truncate text-sm font-semibold text-gray-800 dark:text-gray-100">Report #{report.id}</p>
                  <p className="truncate text-sm text-gray-600 dark:text-gray-300">Created: {new Date(report.created_at).toLocaleDateString()}</p>
                  <p className="truncate text-sm text-gray-600 dark:text-gray-300">Accuracy: <span className="font-bold">{(report.avg_accuracy * 100).toFixed(2)}%</span></p>
                  <p className="truncate text-sm text-gray-600 dark:text-gray-300">Loss: <span className="font-bold">{report.avg_loss.toFixed(4)}</span></p>
                </div>
                <div>
                  <Link href={`/reports/${report.id}`}>
                    View Details
                  </Link>
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default ReportsList;