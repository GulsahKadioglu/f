# -*- coding: utf-8 -*-
"""reports.py

This file defines the API endpoints for managing analysis reports and federated
learning (FL) metrics. It provides functionalities for creating and retrieving
reports, accessing FL round metrics, initiating FL rounds, and triggering
explainable AI (XAI) heatmap generation.

Purpose:
- To allow users to create and view medical analysis reports.
- To provide access to historical federated learning performance metrics.
- To enable administrators to initiate new federated learning rounds.
- To integrate with background tasks (Celery) for computationally intensive operations
  like heatmap generation.

Key Components:
- `APIRouter`: Organizes report and FL metric-related endpoints.
- `crud.report` and `crud.fl_metrics`: Database interaction layers for reports and FL metrics.
- `schemas`: Pydantic models for request and response data validation.
- `backend.core.security`: Dependencies for user authentication and authorization.
- Integration with `backend.worker` for asynchronous task processing.
"""

from typing import List

from .. import crud, schemas
from ..core.security import (
    get_current_admin_user,
    get_current_user,
    get_current_active_user,
)
from ..db.session import get_db
from ..models.fl_metrics import FLRoundMetric
from ..models.user import Permission, User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/", response_model=schemas.Report)
def create_analysis_report(
    report: schemas.ReportCreate,  # Pydantic model for the report details to be created.
    db: Session = Depends(get_db),  # Database session dependency.
    current_user: User = Depends(get_current_user),  # Authenticated user dependency.
):
    """Create a new analysis report.

    This endpoint allows an authenticated user to submit a new analysis report.
    The report details are validated against the `schemas.ReportCreate` Pydantic model.

    Args:
        report (schemas.ReportCreate): The Pydantic model containing the details of the report to be created.
        db (Session): The SQLAlchemy database session.
        current_user (User): The authenticated user object, ensuring the report is associated with a valid user.

    Returns:
        schemas.Report: The newly created report object, conforming to `schemas.Report`.

    """
    return crud.report.create_report(db=db, report=report, owner_id=current_user.id)


@router.get("/", response_model=List[schemas.Report])
def read_reports(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieve analysis reports.

    This endpoint allows an authenticated user to retrieve a paginated list of
    analysis reports. If the user has 'REPORT_VIEW_ALL' permission, all reports
    are returned. Otherwise, only reports owned by the user are returned.
    """
    user_permissions = current_user.role.get_permissions()
    if Permission.REPORT_VIEW_ALL in user_permissions:
        reports = crud.report.get_reports(db, skip=skip, limit=limit)
    elif Permission.REPORT_VIEW_OWN in user_permissions:
        reports = crud.report.get_reports(
            db, user_id=current_user.id, skip=skip, limit=limit
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view reports.",
        )
    return reports


@router.get("/statistics", response_model=schemas.ReportStatistics)
def get_report_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieves aggregated statistics about analysis reports.

    This endpoint provides an overview of the reports, including counts by status,
    average confidence scores, and distribution of diagnosis results.

    Args:
        db (Session): The SQLAlchemy database session.
        current_user (User): The authenticated user object.

    Returns:
        schemas.ReportStatistics: An object containing various aggregated statistics.

    """
    return crud.report.get_report_statistics(db)


@router.get("/fl-metrics", response_model=List[schemas.FLRoundMetric])
def read_fl_metrics(
    db: Session = Depends(get_db),  # Database session dependency.
    current_user: User = Depends(get_current_user),  # Authenticated user dependency.
):
    """Retrieve federated learning round metrics.

    This endpoint provides access to the historical performance metrics of each
    federated learning round. It allows users to monitor the progress and effectiveness
    of the FL model training.

    Args:
        db (Session): The SQLAlchemy database session.
        current_user (User): The authenticated user object. Access to FL metrics
                             is generally allowed for any authenticated user.

    Returns:
        List[schemas.FLRoundMetric]: A list of federated learning round metric objects,
                                     ordered by round number, conforming to `schemas.FLRoundMetric`.

    """
    metrics = db.query(FLRoundMetric).order_by(FLRoundMetric.round_number).all()
    return metrics


@router.post(
    "/start-fl-round",
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(get_current_admin_user)
    ],  # Ensures only admin users can initiate FL rounds.
)
def start_fl_round():
    """Initiates a federated learning round (admin only).

    This endpoint allows an authenticated administrator to trigger the start of a
    new federated learning training round. In a production environment, this would
    typically send a signal or task to the FL server component to begin the process.

    Returns:
        dict: A confirmation message indicating that the request to initiate an FL round has been received.

    """
    from ..worker import start_fl_round_task

    task = start_fl_round_task.delay()
    return {
        "message": "Federated learning round initiation request received.",
        "task_id": task.id,
    }


@router.post("/{report_id}/generate-heatmap", tags=["XAI"])
def trigger_heatmap_generation(
    report_id: str,  # Path parameter: The ID of the report for which to generate a heatmap.
    current_user: User = Depends(get_current_user),  # Authenticated user dependency.
):
    """Triggers heatmap generation for a report in the background.

    This endpoint dispatches an asynchronous task to generate an Explainable AI (XAI)
    heatmap for a specified medical report. The actual heatmap generation is handled
    by a Celery worker (`generate_heatmap_task`) to avoid blocking the API response.

    Args:
        report_id (str): The unique identifier of the report for which the heatmap
                         will be generated. This ID is passed to the background task.
        current_user (User): The authenticated user object. This ensures that only
                             authorized users can request heatmap generation.

    Returns:
        dict: A message indicating that the heatmap generation task has been started
              and the unique ID of the Celery task, which can be used to track its status.

    """
    from ..worker import generate_heatmap_task

    task = generate_heatmap_task.delay(report_id)
    return {"message": "Heatmap generation started.", "task_id": task.id}
