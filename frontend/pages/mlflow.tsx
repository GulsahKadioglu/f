'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import Link from 'next/link';

interface MLflowRun {
  run_uuid: string;
  experiment_id: string;
  run_name: string;
  start_time: string;
  end_time: string;
  lifecycle_stage: string;
}

const MLflowPage = () => {
  const [runs, setRuns] = useState<MLflowRun[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRuns = async () => {
      try {
        const response = await axios.get('/api/v1/mlflow/runs', {
          withCredentials: true, // Important for sending cookies with the request
        });
        setRuns(response.data);
      } catch (err) {
        setError('Failed to fetch MLflow runs. Make sure you are logged in.');
        console.error(err);
      }
    };

    fetchRuns();
  }, []);

  if (error) {
    return <div className="p-4 text-red-500">{error}</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">MLflow Runs</h1>
      <div className="overflow-x-auto">
        <table className="min-w-full bg-white border border-gray-200">
          <thead>
            <tr className="bg-gray-100">
              <th className="py-2 px-4 border-b">Run Name</th>
              <th className="py-2 px-4 border-b">Run UUID</th>
              <th className="py-2 px-4 border-b">Start Time</th>
              <th className="py-2 px-4 border-b">End Time</th>
              <th className="py-2 px-4 border-b">Lifecycle Stage</th>
            </tr>
          </thead>
          <tbody>
            {runs.map((run) => (
              <tr key={run.run_uuid} className="hover:bg-gray-50">
                <td className="py-2 px-4 border-b">
                  <Link href={`/mlflow/${run.run_uuid}`} className="text-blue-600 hover:underline">
                    {run.run_name}
                  </Link>
                </td>
                <td className="py-2 px-4 border-b">{run.run_uuid}</td>
                <td className="py-2 px-4 border-b">{new Date(run.start_time).toLocaleString()}</td>
                <td className="py-2 px-4 border-b">{new Date(run.end_time).toLocaleString()}</td>
                <td className="py-2 px-4 border-b">{run.lifecycle_stage}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default MLflowPage;
