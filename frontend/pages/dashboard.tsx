"use client";

import React, { useEffect, useState } from 'react';
import { apiClient } from '@/services/api';
import dynamic from 'next/dynamic';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { AxiosResponse, AxiosInstance } from 'axios';

const FLChart = dynamic(() => import('@/components/FLChart'), {
  ssr: false,
  loading: () => <p>Loading chart...</p>
});

const DashboardPage = () => {
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [dashboardError, setDashboardError] = useState<any>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const typedApiClient: AxiosInstance = apiClient;
        const response: AxiosResponse<any> = await typedApiClient.get('/dashboard/');
        setDashboardData(response.data);
      } catch (err) {
        setDashboardError(err);
      }
    };
    fetchDashboardData();
  }, []);

  if (dashboardError) return <div className="p-6 text-red-500">Failed to load dashboard data.</div>;
  if (!dashboardData) return <div className="p-6">Loading dashboard...</div>;

  // Prepare data for the FL Metrics chart
  const chartData = {
    labels: dashboardData?.fl_metrics?.map((metric: any) => `Round ${metric.round_number}`) || [],
    datasets: [
      {
        label: 'Accuracy',
        data: dashboardData?.fl_metrics?.map((metric: any) => metric.avg_accuracy) || [],
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1,
      },
      {
        label: 'Loss',
        data: dashboardData?.fl_metrics?.map((metric: any) => metric.avg_loss) || [],
        borderColor: 'rgb(255, 99, 132)',
        tension: 0.1,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Federated Learning Model Performance',
      },
    },
  };

  const cardVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.5
      }
    }
  };

  return (
    <div className="p-6">
      <motion.h1
        className="text-3xl font-bold mb-6"
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        Dashboard
      </motion.h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Widget 1: Cases Awaiting Review */}
        <motion.div
          className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow"
          variants={cardVariants}
          initial="hidden"
          animate="visible"
          transition={{ delay: 0.1 }}
        >
          <h2 className="text-xl font-semibold mb-2">Cases Awaiting Review</h2>
          {dashboardData.cases_awaiting_review.length === 0 ? (
            <p>No cases awaiting review.</p>
          ) : (
            <ul className="list-disc pl-5">
              {dashboardData.cases_awaiting_review.map((caseItem: any) => (
                <li key={caseItem.id} className="mb-1">
                  <Link href={`/cases/${caseItem.id}`} className="text-blue-500 hover:underline">
                      Patient ID: {caseItem.patient_id} (Case ID: {caseItem.id.substring(0, 8)}...)
                    </Link>
                </li>
              ))}
            </ul>
          )}
        </motion.div>

        {/* Widget 2: Model Performance Overview */}
        <motion.div
          className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow col-span-full lg:col-span-2"
          variants={cardVariants}
          initial="hidden"
          animate="visible"
          transition={{ delay: 0.2 }}
        >
          <h2 className="text-xl font-semibold mb-2">Model Performance Overview</h2>
          {dashboardData.fl_metrics.length === 0 ? (
            <p>No FL metrics available.</p>
          ) : (
            <FLChart data={chartData} options={chartOptions} />
          )}
        </motion.div>

        {/* Widget 3: Report Statistics */}
        <motion.div
          className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow"
          variants={cardVariants}
          initial="hidden"
          animate="visible"
          transition={{ delay: 0.3 }}
        >
          <h2 className="text-xl font-semibold mb-2">Report Statistics</h2>
          {dashboardData.report_stats.total_reports === 0 ? (
            <p>No report statistics available.</p>
          ) : (
            <div>
              <p>Total Reports: {dashboardData.report_stats.total_reports}</p>
              <p>Avg Confidence: {dashboardData.report_stats.average_confidence_score?.toFixed(2)}</p>
            </div>
          )}
        </motion.div>

        {/* Widget 4: Recent Reports */}
        <motion.div
          className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow"
          variants={cardVariants}
          initial="hidden"
          animate="visible"
          transition={{ delay: 0.4 }}
        >
          <h2 className="text-xl font-semibold mb-2">Recent Reports</h2>
          {dashboardData.recent_reports.length === 0 ? (
            <p>No recent reports.</p>
          ) : (
            <ul className="list-disc pl-5">
              {dashboardData.recent_reports.map((report: any) => (
                <li key={report.id} className="mb-1">
                  Report ID: {report.id.substring(0, 8)}... (Confidence: {report.final_confidence_score?.toFixed(2)})
                </li>
              ))}
            </ul>
          )}
        </motion.div>

      </div>
    </div>
  );
};

export default DashboardPage;