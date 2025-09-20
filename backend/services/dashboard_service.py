# -*- coding: utf-8 -*-
"""
dashboard_service.py

This service provides the business logic for aggregating data required by the
dashboard. It fetches information from various parts of the application,
such as medical cases, federated learning metrics, and reports, and
structures it into a format suitable for the dashboard's frontend.

Purpose:
- To act as an intermediary between the API layer and the data access layer (CRUD).
- To gather and process data from multiple sources for a unified dashboard view.
- To decouple the dashboard's data requirements from the underlying database queries.

Key Components:
- `get_dashboard_data`: The primary function that compiles all necessary data
  for the dashboard.
"""

from sqlalchemy.orm import Session

from backend import crud
from backend.schemas.dashboard import (
    CaseInfo,
    DashboardData,
    FLMetric,
    RecentReport,
    ReportStats,
)


def get_dashboard_data(db: Session) -> DashboardData:
    """
    Aggregates and returns all data required for the main dashboard view.

    This function fetches various pieces of information from the database via the
    CRUD layer, converts them into their corresponding Pydantic schemas, and
    assembles them into a single `DashboardData` object.

    Args:
        db (Session): The SQLAlchemy database session.

    Returns:
        DashboardData: A Pydantic model containing structured data for the dashboard,
                       including cases awaiting review, FL metrics, report statistics,
                       and recent reports.
    """
    # Fetch data from different CRUD modules
    cases_awaiting_review_db = crud.medical_case.get_multi(
        db, status="awaiting_review", limit=5
    )
    fl_metrics_db = crud.fl_metric.get_multi(db, limit=10)  # Get last 10 rounds
    report_stats_db = crud.report.get_statistics(db)
    recent_reports_db = crud.report.get_multi(db, limit=5)

    # Convert DB objects to Pydantic models
    cases_awaiting_review = [CaseInfo.from_orm(c) for c in cases_awaiting_review_db]
    fl_metrics = [FLMetric.from_orm(m) for m in fl_metrics_db]
    report_stats = ReportStats.from_orm(report_stats_db)
    recent_reports = [RecentReport.from_orm(r) for r in recent_reports_db]

    return DashboardData(
        cases_awaiting_review=cases_awaiting_review,
        fl_metrics=fl_metrics,
        report_stats=report_stats,
        recent_reports=recent_reports,
    )