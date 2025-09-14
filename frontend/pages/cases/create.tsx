"use client";

/**
 * @file frontend/src/app/cases/create/page.tsx
 * @description This Next.js page provides a form for creating a new medical case.
 * It allows users to input patient ID, case date, and status, and then
 * sends this data to the backend API.
 */

import React, { useState } from 'react';
import { useRouter } from 'next/router';
import { apiClient } from '@/services/api';
import { AxiosResponse, AxiosInstance } from 'axios';

/**
 * CreateCasePage component.
 *
 * This component renders a form for creating a new medical case. It manages
 * the form's state, handles submission, and interacts with the backend API.
 * Upon successful creation, it navigates the user back to the cases list.
 *
 * @returns {JSX.Element} The Create Case page.
 */
export default function CreateCasePage() {
  const [patientId, setPatientId] = useState<string>('');
  const [caseDate, setCaseDate] = useState<string>('');
  const [status, setStatus] = useState<string>('Active'); // Default status
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  /**
   * Handles the form submission for creating a new case.
   *
   * Prevents default form submission, sets loading state, and sends a POST
   * request to the backend. Handles success by navigating, and errors by
   * setting an error message.
   *
   * @param {React.FormEvent} e - The form event.
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const typedApiClient: AxiosInstance = apiClient;
      const response: AxiosResponse<any> = await typedApiClient.post('/api/v1/cases/', {
        patient_id: patientId,
        case_date: caseDate,
        status: status,
      });
      console.log('New case created:', response.data);
      router.push('/cases'); // Navigate back to the cases list
    } catch (err) {
      setError('An error occurred while creating the case.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-2xl mx-auto bg-white p-8 rounded-lg shadow-md">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">Create New Case</h1>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Patient ID Input */}
          <div>
            <label htmlFor="patientId" className="block text-sm font-medium text-gray-700">Patient ID</label>
            <input
              type="text"
              id="patientId"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              value={patientId}
              onChange={(e) => setPatientId(e.target.value)}
              required
            />
          </div>

          {/* Case Date Input */}
          <div>
            <label htmlFor="caseDate" className="block text-sm font-medium text-gray-700">Case Date</label>
            <input
              type="date"
              id="caseDate"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              value={caseDate}
              onChange={(e) => setCaseDate(e.target.value)}
              required
            />
          </div>

          {/* Status Select */}
          <div>
            <label htmlFor="status" className="block text-sm font-medium text-gray-700">Status</label>
            <select
              id="status"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              value={status}
              onChange={(e) => setStatus(e.target.value)}
            >
              <option value="Active">Active</option>
              <option value="Pending">Pending</option>
              <option value="Closed">Closed</option>
            </select>
          </div>

          {/* Error Message */}
          {error && <p className="text-red-500 text-sm">{error}</p>}

          {/* Submit Button */}
          <button
            type="submit"
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            disabled={loading}
          >
            {loading ? 'Creating...' : 'Create Case'}
          </button>
        </form>
      </div>
    </main>
  );
}