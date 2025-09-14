"use client";

import React from 'react';
import CasesList from '../src/components/CasesList';

const CasesPage = () => {
  return (
    <main className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-800 mb-8">Case Management</h1>
        <div className="bg-white p-6 rounded-lg shadow-md">
          <CasesList />
        </div>
      </div>
    </main>
  );
};

export default CasesPage;