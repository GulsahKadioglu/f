"use client";

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { apiClient } from '@/services/api';
import { AxiosResponse, AxiosInstance } from 'axios';

const CaseDetailPage = () => {
  const router = useRouter();
  const { case_id } = router.query;

  const [caseData, setCaseData] = useState<any>(null);
  const [caseError, setCaseError] = useState<any>(null);

  useEffect(() => {
    if (case_id) {
      const fetchCaseData = async () => {
        try {
          const typedApiClient: AxiosInstance = apiClient;
          const response: AxiosResponse<any> = await typedApiClient.get(`/medical-cases/${case_id}`);
          setCaseData(response.data);
        } catch (err) {
          setCaseError(err);
        }
      };
      fetchCaseData();
    }
  }, [case_id]);

  if (caseError) return <div className="p-6 text-red-500">Error loading case details.</div>;
  if (!caseData) return <div className="p-6">Loading case details...</div>;

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Case Details: {caseData.patient_id}</h1>
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow mb-6">
        <h2 className="text-xl font-semibold mb-2">Case Information</h2>
        <p><strong>Case ID:</strong> {caseData.id}</p>
        <p><strong>Patient ID:</strong> {caseData.patient_id}</p>
        <p><strong>Status:</strong> {caseData.status}</p>
        <p><strong>Doctor ID:</strong> {caseData.doctor_id}</p>
        <p><strong>Created At:</strong> {new Date(caseData.created_at).toLocaleString()}</p>
      </div>

      <h2 className="text-2xl font-bold mb-4">Medical Images</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {caseData.images && caseData.images.length > 0 ? (
          caseData.images.map((image: any) => (
            <div key={image.id} className="bg-white dark:bg-gray-800 p-2 rounded-lg shadow">
              <img src={image.image_path} alt={`Medical Image ${image.id}`} className="w-full h-auto object-contain" />
              <p className="text-sm mt-2">Uploaded: {new Date(image.upload_timestamp).toLocaleString()}</p>
            </div>
          ))
        ) : (
          <p>No medical images found for this case.</p>
        )}
      </div>
    </div>
  );
};

export default CaseDetailPage;