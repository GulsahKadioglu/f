"use client";

import React, { useEffect, useState, useMemo } from "react";
import { useRouter } from "next/router";
import { apiClient } from "@/services/api";
import Link from "next/link";
import { AxiosResponse, AxiosInstance } from "axios";

interface Case {
  id: number;
  patient_id: string;
  case_date: string;
  status: string;
}

const columns = [
  { key: "id", label: "CASE ID" },
  { key: "patient_id", label: "PATIENT ID" },
  { key: "case_date", label: "CASE DATE" },
  { key: "status", label: "STATUS" },
  { key: "actions", label: "ACTIONS" },
];

const statusOptions = [
  { label: "All", value: "" },
  { label: "Active", value: "Active" },
  { label: "Pending", value: "Pending" },
  { label: "Closed", value: "Closed" },
];

export default function CasesList() {
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const [sortDescriptor, setSortDescriptor] = useState<{
    column: string;
    direction: "ascending" | "descending";
  }>({
    column: "case_date",
    direction: "descending",
  });
  const [filterStatus, setFilterStatus] = useState<string>("");

  useEffect(() => {
    const fetchCases = async () => {
      try {
        setLoading(true);
        const params = new URLSearchParams();
        if (sortDescriptor.column) {
          params.append("sort_by", sortDescriptor.column.toString());
          params.append(
            "sort_order",
            sortDescriptor.direction === "ascending" ? "asc" : "desc"
          );
        }
        if (filterStatus) {
          params.append("status", filterStatus);
        }
        const typedApiClient: AxiosInstance = apiClient;
        const response: AxiosResponse<Case[]> =
          await typedApiClient.get<Case[]>(
            `/api/v1/cases/?${params.toString()}`
          );
        setCases(response.data);
      } catch (err) {
        setError("An error occurred while loading cases.");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchCases();
  }, [sortDescriptor, filterStatus]);

  const sortedItems = useMemo(() => {
    // This sorting logic should ideally be handled by the backend for large datasets
    // For now, we'll sort on the frontend.
    const sorted = [...cases].sort((a, b) => {
      const aValue = a[sortDescriptor.column as keyof Case];
      const bValue = b[sortDescriptor.column as keyof Case];

      if (typeof aValue === "string" && typeof bValue === "string") {
        return sortDescriptor.direction === "ascending"
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      } else if (typeof aValue === "number" && typeof bValue === "number") {
        return sortDescriptor.direction === "ascending"
          ? aValue - bValue
          : bValue - aValue;
      }
      return 0;
    });
    return sorted;
  }, [cases, sortDescriptor]);

  const renderCell = React.useCallback((item: Case, columnKey: React.Key) => {
    const cellValue = item[columnKey as keyof Case];

    switch (columnKey) {
      case "case_date":
        return new Date(cellValue).toLocaleDateString();
      case "actions":
        return (
          <Link href={`/cases/${item.id}`}>
            View Details
          </Link>
        );
      default:
        return cellValue;
    }
  }, []);

  const handleSort = (columnKey: string) => {
    if (sortDescriptor.column === columnKey) {
      setSortDescriptor({
        ...sortDescriptor,
        direction:
          sortDescriptor.direction === "ascending" ? "descending" : "ascending",
      });
    } else {
      setSortDescriptor({
        column: columnKey,
        direction: "ascending",
      });
    }
  };

  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg border border-slate-200 dark:border-slate-700">
      {/* Card Header */}
      <div className="flex flex-col sm:flex-row justify-between items-center gap-4 p-6 border-b border-slate-200 dark:border-slate-700">
        <h2 className="text-xl font-bold text-slate-800 dark:text-slate-100">
          Case Management
        </h2>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <label
              htmlFor="status-select"
              className="text-sm font-medium text-slate-600 dark:text-slate-300"
            >
              Status:
            </label>
            <select
              id="status-select"
              className="block w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm dark:bg-slate-700 dark:border-slate-600 dark:text-white dark:focus:border-blue-500"
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
            >
              {statusOptions.map((status) => (
                <option key={status.value} value={status.value}>
                  {status.label}
                </option>
              ))}
            </select>
          </div>
          <Link href="/cases/create">
            Create Case
          </Link>
        </div>
      </div>

      {/* Card Body */}
      <div className="p-6">
        {error ? (
          <div className="text-center text-red-600 p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
            {error}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead className="bg-slate-50 dark:bg-slate-700">
                <tr>
                  {columns.map((column) => (
                    <th
                      key={column.key}
                      scope="col"
                      className="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-300 uppercase tracking-wider cursor-pointer"
                      onClick={() =>
                        column.key !== "actions" && handleSort(column.key)
                      }
                    >
                      {column.label}
                      {column.key === sortDescriptor.column && (
                        <span className="ml-1">
                          {sortDescriptor.direction === "ascending" ? "▲" : "▼"}
                        </span>
                      )}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-200 dark:bg-slate-800 dark:divide-slate-700">
                {loading ? (
                  <tr>
                    <td
                      colSpan={columns.length}
                      className="text-center py-10 text-slate-500 dark:text-slate-400"
                    >
                      Loading cases...
                    </td>
                  </tr>
                ) : sortedItems.length === 0 ? (
                  <tr>
                    <td
                      colSpan={columns.length}
                      className="text-center py-10 text-slate-500 dark:text-slate-400"
                    >
                      No cases found.
                    </td>
                  </tr>
                ) : (
                  sortedItems.map((item) => (
                    <tr
                      key={item.id}
                      className="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors duration-150"
                    >
                      {columns.map((column) => (
                        <td
                          key={column.key}
                          className="px-6 py-4 whitespace-nowrap text-sm text-slate-700 dark:text-slate-200"
                        >
                          {renderCell(item, column.key)}
                        </td>
                      ))}
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
