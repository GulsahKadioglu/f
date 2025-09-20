# -*- coding: utf-8 -*-
"""
dashboard.py

This file defines the API endpoint for fetching all data required by the
main dashboard in a single request. It acts as a high-level aggregator,
relying on the `dashboard_service` to collect and structure the data.

Purpose:
- To provide a single, efficient endpoint for the frontend dashboard to consume.
- To decouple the API endpoint from the underlying data-gathering logic.
- To ensure that only active, authenticated users can access dashboard data.

Key Components:
- `APIRouter`: Organizes the dashboard-related endpoint.
- `dashboard_service.get_dashboard_data`: The service function that performs
  the actual data aggregation.
- `deps.get_current_active_user`: Dependency to ensure the user is authenticated
  and active.
"""

from backend import deps
from backend.models.user import User
from backend.schemas.dashboard import DashboardData
from backend.services import dashboard_service
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/", response_model=DashboardData)
def read_dashboard_data(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> DashboardData:
    """
    Retrieve consolidated data for the main dashboard.

    This endpoint aggregates various data points from different parts of the
    application to provide a complete snapshot for the dashboard view. It fetches
    cases awaiting review, federated learning metrics, report statistics, and
    recent reports by calling the `dashboard_service`.

    Args:
        db (Session): The database session dependency.
        current_user (User): The currently authenticated active user.

    Returns:
        DashboardData: A Pydantic model containing all the structured data
                       required to populate the dashboard.
    """
    return dashboard_service.get_dashboard_data(db=db)