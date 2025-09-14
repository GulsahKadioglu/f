// frontend/src/app/patient-portal/page.tsx
// This page will serve as the main entry point for the patient portal.

import React from 'react';
import Link from 'next/link';

const PatientPortalPage = () => {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Patient Portal Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="max-w-[400px]">
          <div className="flex gap-3">
            <img
              alt="patient icon"
              src="/images/patient-icon.png" // Placeholder image
              width={40}
              height={40}
            />
            <div className="flex flex-col">
              <p className="text-md">My Profile</p>
              <p className="text-small text-default-500">View and edit your personal information.</p>
            </div>
          </div>
          <hr />
          <div>
            <p>Access your demographic details, contact information, and preferences.</p>
          </div>
          <hr />
          <div>
            <Link href="/profile">
              Go to Profile
            </Link>
          </div>
        </div>

        <div className="max-w-[400px]">
          <div className="flex gap-3">
            <img
              alt="cases icon"
              src="/images/cases-icon.png" // Placeholder image
              width={40}
              height={40}
            />
            <div className="flex flex-col">
              <p className="text-md">My Medical Cases</p>
              <p className="text-small text-default-500">Review your medical history and case details.</p>
            </div>
          </div>
          <hr />
          <div>
            <p>View a list of all your medical cases, including diagnoses and treatments.</p>
          </div>
          <hr />
          <div>
            <Link href="/cases">
              View Cases
            </Link>
          </div>
        </div>

        <div className="max-w-[400px]">
          <div className="flex gap-3">
            <img
              alt="reports icon"
              src="/images/reports-icon.png" // Placeholder image
              width={40}
              height={40}
            />
            <div className="flex flex-col">
              <p className="text-md">My Reports</p>
              <p className="text-small text-default-500">Access your medical reports and lab results.</p>
            </div>
          </div>
          <hr />
          <div>
            <p>Download and review your medical reports, including lab results and imaging reports.</p>
          </div>
          <hr />
          <div>
            <Link href="/reports">
              View Reports
            </Link>
          </div>
        </div>
      </div>
      <div className="mt-8">
        <h2 className="text-2xl font-semibold mb-4">Quick Actions</h2>
        <div className="flex gap-4">
          <button>
            Upload New Data
          </button>
          <button>
            Contact Support
          </button>
        </div>
      </div>
    </div>
  );
};

export default PatientPortalPage;
