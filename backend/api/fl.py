# -*- coding: utf-8 -*-
"""fl.py

This file defines the API endpoints related to the Federated Learning (FL) process.
It provides endpoints for clients to fetch the encryption context needed for secure
aggregation and for the FL server to post back round metrics.

Purpose:
- To facilitate the secure and coordinated execution of the federated learning
  process.
- To provide FL clients (nodes) with the necessary cryptographic context to
  participate in secure aggregation.
- To allow the central FL server to store and manage performance metrics for
  each training round.

Key Components:
- `/context`: Endpoint for FL clients to retrieve the public TenSEAL context for
  encrypting their model updates.
- `/metrics`: A set of CRUD endpoints for managing `FLRoundMetric` records,
  allowing the FL server to post new metrics and administrators to view or
  manage them.
"""

from typing import List

from backend import encryption_service, schemas
from backend.core.security import (
    get_current_admin_user,
    get_current_user,
)
from backend.crud import fl_metric as crud_fl_metric
from backend.db.session import get_db
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

router = APIRouter()


@router.get(
    "/context", response_model=schemas.EncryptionContext, tags=["Federated Learning"]
)
async def get_fl_context(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    """Retrieves the federated learning encryption context.

    This endpoint provides the necessary encryption parameters (e.g., TenSEAL context)
    that federated learning clients (nodes) need to encrypt their model updates
    before sending them to the central server. This ensures privacy-preserving
    aggregation of model weights.

    Requires authentication.
    """
    context_bytes = encryption_service.get_public_context()
    return schemas.EncryptionContext(context=context_bytes)


@router.post(
    "/metrics", response_model=schemas.FLRoundMetric, tags=["Federated Learning"]
)
async def create_fl_metric(
    fl_metric_in: schemas.FLRoundMetricBase,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_admin_user),
):
    """Receives and stores federated learning metrics from the FL server.

    This endpoint is intended to be called by the central Flower server
    or a trusted component that aggregates metrics from FL rounds.
    It stores metrics like loss, accuracy, and round number in the database
    for monitoring and visualization.

    Requires authentication.
    """
    metric = crud_fl_metric.create(db, obj_in=fl_metric_in)
    return metric


@router.get(
    "/metrics", response_model=List[schemas.FLRoundMetric], tags=["Federated Learning"]
)
async def get_fl_metrics(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    """Retrieves all federated learning metrics.

    Allows administrators or authorized users to view the historical
    performance and progress of federated learning rounds.

    Requires authentication.
    """
    metrics = crud_fl_metric.get_all(db)
    return metrics


@router.get(
    "/metrics/latest", response_model=schemas.FLRoundMetric, tags=["Federated Learning"]
)
async def get_latest_fl_metric(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    """Retrieves the latest federated learning metric.

    Useful for dashboards or real-time monitoring to display the most recent
    performance update from the federated learning process.

    Requires authentication.
    """
    latest_metric = crud_fl_metric.get_latest(db)
    if not latest_metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No FL metrics found."
        )
    return latest_metric


@router.get(
    "/metrics/round/{round_num}",
    response_model=schemas.FLRoundMetric,
    tags=["Federated Learning"],
)
async def get_fl_metric_by_round(
    round_num: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    """Retrieves a specific federated learning metric by round number.

    Allows for detailed inspection of FL performance at a particular training round.

    Requires authentication.
    """
    metric = crud_fl_metric.get_by_round(db, round_num=round_num)
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"FL metric for round {round_num} not found.",
        )
    return metric


@router.delete(
    "/metrics/{metric_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Federated Learning"],
)
async def delete_fl_metric(
    metric_id: int,
    db: Session = Depends(get_db),
    current_admin_user: schemas.User = Depends(get_current_admin_user),
):
    """Deletes a federated learning metric by its ID.

    This is an administrative operation to manage FL metric records.

    Requires authentication as an admin user.
    """
    metric = crud_fl_metric.get(db, id=metric_id)
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="FL metric not found."
        )
    crud_fl_metric.remove(db, id=metric_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put(
    "/metrics/{metric_id}",
    response_model=schemas.FLRoundMetric,
    tags=["Federated Learning"],
)
async def update_fl_metric(
    metric_id: int,
    fl_metric_in: schemas.FLRoundMetricUpdate,
    db: Session = Depends(get_db),
    current_admin_user: schemas.User = Depends(get_current_admin_user),
):
    """Updates an existing federated learning metric by its ID.

    This is an administrative operation to correct or modify FL metric records.

    Requires authentication as an admin user.
    """
    metric = crud_fl_metric.get(db, id=metric_id)
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="FL metric not found."
        )
    metric = crud_fl_metric.update(db, db_obj=metric, obj_in=fl_metric_in)
    return metric