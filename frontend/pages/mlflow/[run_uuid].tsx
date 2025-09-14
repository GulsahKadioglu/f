'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { useRouter } from 'next/router';
import dynamic from 'next/dynamic';

const FLChart = dynamic(() => import('@/components/FLChart'), {
  ssr: false,
  loading: () => <p>Loading chart...</p>
});

interface MLflowParam {
  key: string;
  value: string;
}

interface MLflowMetric {
  key: string;
  value: number;
  timestamp: number;
  step: number;
}

interface MLflowArtifact {
  path: string;
  is_dir: boolean;
  file_size: number | null;
}

interface MLflowRunDetail {
  run_uuid: string;
  experiment_id: string;
  run_name: string;
  start_time: string;
  end_time: string;
  lifecycle_stage: string;
  params: MLflowParam[];
  metrics: { [key: string]: MLflowMetric[] };
  artifacts: MLflowArtifact[];
}

const RunDetailPage = () => {
  const router = useRouter();
  const { run_uuid } = router.query;
  const [runDetail, setRunDetail] = useState<MLflowRunDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (run_uuid) {
      const fetchRunDetail = async () => {
        try {
          const response = await axios.get(`/api/v1/mlflow/runs/${run_uuid}`, {
            withCredentials: true,
          });
          setRunDetail(response.data);
        } catch (err) {
          setError('Failed to fetch run details. Make sure you are logged in.');
          console.error(err);
        }
      };
      fetchRunDetail();
    }
  }, [run_uuid]);

  if (error) {
    return <div className="p-4 text-red-500">{error}</div>;
  }

  if (!runDetail) {
    return <div className="p-4">Loading...</div>;
  }

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  const getChartData = (metricKey: string) => {
    const metricHistory = runDetail.metrics[metricKey];
    if (!metricHistory || metricHistory.length === 0) {
      return null;
    }

    const labels = metricHistory.map(m => m.step);
    const data = metricHistory.map(m => m.value);

    return {
      labels,
      datasets: [
        {
          label: metricKey,
          data,
          fill: false,
          borderColor: 'rgb(75, 192, 192)',
          tension: 0.1,
        },
      ],
    };
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Run: {runDetail.run_name || runDetail.run_uuid}</h1>
      <div className="bg-white shadow-md rounded-lg p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Run Info</h2>
        <p><strong>Run UUID:</strong> {runDetail.run_uuid}</p>
        <p><strong>Experiment ID:</strong> {runDetail.experiment_id}</p>
        <p><strong>Start Time:</strong> {formatTimestamp(runDetail.start_time)}</p>
        <p><strong>End Time:</strong> {runDetail.end_time ? formatTimestamp(runDetail.end_time) : 'N/A'}</p>
        <p><strong>Lifecycle Stage:</strong> {runDetail.lifecycle_stage}</p>
      </div>

      {runDetail.params.length > 0 && (
        <div className="bg-white shadow-md rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Parameters</h2>
          <table className="min-w-full bg-white border border-gray-200">
            <thead>
              <tr className="bg-gray-100">
                <th className="py-2 px-4 border-b">Key</th>
                <th className="py-2 px-4 border-b">Value</th>
              </tr>
            </thead>
            <tbody>
              {runDetail.params.map(param => (
                <tr key={param.key} className="hover:bg-gray-50">
                  <td className="py-2 px-4 border-b">{param.key}</td>
                  <td className="py-2 px-4 border-b">{param.value}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {Object.keys(runDetail.metrics).length > 0 && (
        <div className="bg-white shadow-md rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Metrics</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Object.keys(runDetail.metrics).map(metricKey => {
              const chartData = getChartData(metricKey);
              return chartData ? (
                <div key={metricKey} className="bg-gray-50 p-4 rounded-lg shadow-sm">
                  <h3 className="text-lg font-medium mb-2">{metricKey}</h3>
                  <FLChart data={chartData} options={{}} />
                </div>
              ) : null;
            })}
          </div>
        </div>
      )}

      {runDetail.artifacts.length > 0 && (
        <div className="bg-white shadow-md rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Artifacts</h2>
          <ul>
            {runDetail.artifacts.map(artifact => (
              <li key={artifact.path} className="mb-1">
                {artifact.is_dir ? 'â– ' : 'â—‹'} {artifact.path} {artifact.file_size !== null ? `(${artifact.file_size} bytes)` : ''}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default RunDetailPage;
