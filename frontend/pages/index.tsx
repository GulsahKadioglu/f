/**
 * @file frontend/src/app/page.tsx
 * @description This is the main home page of the Next.js application.
 * It serves as a dashboard, integrating and displaying lists of analysis reports
 * and medical cases using reusable components.
 */

import React from 'react';
import Head from 'next/head';
import ReportsList from '../src/components/ReportsList';
import dynamic from 'next/dynamic';

const CasesList = dynamic(() => import('../src/components/CasesList'), { ssr: false });

/**
 * Home component.
 *
 * This component renders the main dashboard of the application. It includes
 * a header with the application title and a brief description, and two main
 * sections: "Analysis Reports" and "Case Management", each displaying a list
 * of relevant items.
 *
 * @returns {JSX.Element} The main home page.
 */
export default function Home() {
  return (
    <main className="min-h-screen bg-gray-100 p-8">
      <Head>
        <title>Federated Cancer Screening</title>
      </Head>
      <div className="max-w-7xl mx-auto">
        {/* Header Section */}
        <header className="mb-12">
          <h1 className="text-4xl font-bold text-gray-800">Cancer Screening Dashboard</h1>
          <p className="text-lg text-gray-600 mt-2">Federated Learning Powered Analysis and Case Management</p>
        </header>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Analysis Reports Section */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-700 mb-4">Analysis Reports</h2>
            <div className="bg-white p-6 rounded-lg shadow-md">
              <ReportsList />
            </div>
          </section>

          {/* Case Management Section */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-700 mb-4">Cases</h2>
            <div className="bg-white p-6 rounded-lg shadow-md">
              <CasesList />
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}
