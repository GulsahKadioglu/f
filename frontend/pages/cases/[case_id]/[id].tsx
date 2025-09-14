import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { apiClient } from '@/services/api';
import { AxiosResponse, AxiosInstance } from 'axios';

export default function CaseDetailPage() {
  const router = useRouter();
  const { id } = router.query;

  const [caseDetail, setCaseDetail] = useState<any>(null);
  const [caseError, setCaseError] = useState<any>(null);
  const [imagesData, setImagesData] = useState<any>(null);
  const [imagesError, setImagesError] = useState<any>(null);

  useEffect(() => {
    if (id) {
      const fetchCaseDetails = async () => {
        try {
          const typedApiClient: AxiosInstance = apiClient;
          const caseResponse: AxiosResponse<any> = await typedApiClient.get(`/api/v1/cases/${id}`);
          setCaseDetail(caseResponse.data);

          const imagesResponse: AxiosResponse<any> = await typedApiClient.get(`/api/v1/cases/${id}/images`);
          setImagesData(imagesResponse.data);
        } catch (err) {
          setCaseError(err);
          setImagesError(err);
        }
      };
      fetchCaseDetails();
    }
  }, [id]);

  if (caseError || imagesError) return <div>Failed to load case data.</div>;
  if (!caseDetail || !imagesData) return <div>Loading...</div>;

  const studyInstanceUID = imagesData && imagesData.length > 0 ? imagesData[0].study_instance_uid : null;

  return (
    <main className="h-screen bg-gray-100 dark:bg-gray-900 flex flex-col p-4">
      <h1 className="text-3xl font-bold mb-4 text-gray-900 dark:text-white">Case Detail</h1>
      <div className="flex-grow border rounded-lg shadow-md bg-white dark:bg-gray-800 flex"> {/* Replaced PanelGroup */}
        <div className="w-1/3 p-4 overflow-auto"> {/* Replaced Panel */}
          <div className="h-full">
            <div>
              <h2 className="text-2xl font-bold">Case #{caseDetail.id.substring(0, 8)}...</h2>
            </div>
            <div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="font-semibold">Patient ID:</p>
                  <p>{caseDetail.patient_id}</p>
                </div>
                <div>
                  <p className="font-semibold">Case Date:</p>
                  <p>{new Date(caseDetail.case_date).toLocaleDateString()}</p>
                </div>
                <div>
                  <p className="font-semibold">Status:</p>
                  <span>
                    {caseDetail.status}
                  </span>
                </div>
              </div>
              <div className="mt-4">
                <p className="font-semibold">Description:</p>
                <p>{caseDetail.description || 'No description provided.'}</p>
              </div>
            </div>
          </div>
        </div>
        <div className="w-2 bg-gray-200 dark:bg-gray-700"></div> {/* Replaced PanelResizeHandle */}
        <div className="w-2/3 bg-black"> {/* Replaced Panel */}
          {studyInstanceUID && (
            <iframe
              src={`/ohif/index.html?StudyInstanceUIDs=${studyInstanceUID}`}
              className="w-full h-full border-0"
            ></iframe>
          )}
        </div>
      </div>
    </main>
  );
}