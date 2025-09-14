# -*- coding: utf-8 -*-
"""dashboard.py

This file defines the Pydantic schemas for the data structures used in the
dashboard API. These schemas are used for data validation, serialization,
and documentation of the dashboard's data models.

Purpose:
- To define the shape and data types of the information displayed on the dashboard.
- To ensure that data passed to and from the dashboard API conforms to a
  strict, predefined structure.
- To provide clear and automatic API documentation for the dashboard endpoint.

Key Components:
- `CaseInfo`: A schema for basic information about a medical case.
- `FLMetric`: A schema for key metrics from a federated learning round.
- `ReportStats`: A schema for aggregated statistics about analysis reports.
- `RecentReport`: A schema for displaying brief details of a recent report.
- `DashboardData`: The main schema that aggregates all other dashboard-related
  data structures into a single response model.
"""

from typing import List, Optional

from pydantic import BaseModel


class CaseInfo(BaseModel):
    """Schema for basic information about a medical case, used for listings."""
    id: str
    patient_id: str


class FLMetric(BaseModel):
    """Schema for essential metrics from a single federated learning round."""
    round_number: int
    avg_accuracy: float
    avg_loss: float


class ReportStats(BaseModel):
    """Schema for aggregated statistics about all analysis reports."""
    total_reports: int
    average_confidence_score: Optional[float]


class RecentReport(BaseModel):
    """Schema for displaying brief details of a recently created report."""
    id: str
    final_confidence_score: Optional[float]


class DashboardData(BaseModel):
    """The main schema that aggregates all data for the dashboard view."""
    cases_awaiting_review: List[CaseInfo]
    fl_metrics: List[FLMetric]
    report_stats: ReportStats
    recent_reports: List[RecentReport]
