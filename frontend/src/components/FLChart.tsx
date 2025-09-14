/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

// Define props type for the component
interface FLChartProps {
  data: any;
  options: any;
}

export default function FLChart({ data, options }: FLChartProps) {
  return <Line data={data} options={options} />;
}
