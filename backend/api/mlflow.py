# -*- coding: utf-8 -*-
"""mlflow.py

This file defines the API endpoints for interacting with MLflow experiment data.
It provides a read-only interface to MLflow runs, allowing users to list runs
and view the details of a specific run, including parameters, metrics, and artifacts.
This is achieved by directly parsing the MLflow experiment files on the filesystem.

Purpose:
- To expose MLflow experiment tracking data via the application's API.
- To allow for the integration of MLflow's results into the main application's
  frontend or for programmatic access.
- To avoid a direct dependency on the MLflow server for read-only operations.

Key Components:
- `/runs`: Lists all active MLflow runs from the default experiment directory.
- `/runs/{run_uuid}`: Fetches detailed information for a single MLflow run,
  including its metadata, parameters, metrics history, and artifacts.
"""

import datetime
import os
from typing import List

import yaml
from .. import schemas
from ..core.security import has_permission
from ..db.session import get_db
from ..models.user import Permission, User
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter()

MLRUNS_PATH = "fl-node/mlruns/0"


@router.get("/runs", response_model=List[schemas.MLflowRun])
def list_mlflow_runs(
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission(Permission.VIEW_FL_METRICS)),
):
    """
    Lists all MLflow runs for the default experiment (experiment_id=0).

    This endpoint scans the MLflow runs directory, reads the `meta.yaml` file
    for each run, and returns a list of run metadata. It automatically filters
    out any runs that have been marked as "deleted".

    Args:
        db (Session): The database session dependency.
        current_user (User): The authenticated user, with required permissions.

    Returns:
        List[schemas.MLflowRun]: A list of MLflow run objects, each containing
                                 basic metadata like run UUID, name, and start time.
    """
    if not os.path.exists(MLRUNS_PATH):
        return []

    runs = []
    for run_uuid in os.listdir(MLRUNS_PATH):
        run_path = os.path.join(MLRUNS_PATH, run_uuid)
        meta_path = os.path.join(run_path, "meta.yaml")
        if os.path.isdir(run_path) and os.path.exists(meta_path):
            with open(meta_path, "r") as f:
                meta = yaml.safe_load(f)
                if meta.get("lifecycle_stage", "active") == "deleted":
                    continue
                runs.append(
                    schemas.MLflowRun(
                        run_uuid=meta.get("run_uuid"),
                        experiment_id=meta.get("experiment_id"),
                        run_name=meta.get("run_name"),
                        start_time=meta.get("start_time"),
                        end_time=meta.get("end_time"),
                        lifecycle_stage=meta.get("lifecycle_stage"),
                    )
                )
    return runs


@router.get("/runs/{run_uuid}", response_model=schemas.MLflowRunDetail)
def get_mlflow_run_detail(
    run_uuid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission(Permission.VIEW_FL_METRICS)),
):
    """
    Retrieves detailed information for a specific MLflow run.

    This endpoint fetches comprehensive details for a single run by its UUID.
    It parses the run's `meta.yaml` file, all parameter files, all metric
    history files, and lists all associated artifacts from the filesystem.

    Args:
        run_uuid (str): The UUID of the MLflow run to retrieve.
        db (Session): The database session dependency.
        current_user (User): The authenticated user, with required permissions.

    Returns:
        schemas.MLflowRunDetail: A detailed MLflow run object, including metadata,
                                 parameters, full metric histories, and a list of
                                 artifacts.

    Raises:
        HTTPException: If the specified run UUID is not found or if its
                       metadata is missing.
    """
    run_path = os.path.join(MLRUNS_PATH, run_uuid)
    if not os.path.exists(run_path) or not os.path.isdir(run_path):
        raise HTTPException(status_code=404, detail="MLflow run not found")

    # Read meta.yaml
    meta_path = os.path.join(run_path, "meta.yaml")
    if not os.path.exists(meta_path):
        raise HTTPException(status_code=404, detail="MLflow run metadata not found")
    with open(meta_path, "r") as f:
        meta = yaml.safe_load(f)

    # Read params
    params_path = os.path.join(run_path, "params")
    params = []
    if os.path.exists(params_path) and os.path.isdir(params_path):
        for param_file in os.listdir(params_path):
            with open(os.path.join(params_path, param_file), "r") as f:
                params.append(schemas.MLflowParam(key=param_file, value=f.read()))

    # Read metrics
    metrics_path = os.path.join(run_path, "metrics")
    metrics = {}
    if os.path.exists(metrics_path) and os.path.isdir(metrics_path):
        for metric_file in os.listdir(metrics_path):
            metric_history = []
            with open(os.path.join(metrics_path, metric_file), "r") as f:
                for line in f:
                    parts = line.strip().split(" ")
                    if len(parts) == 3:
                        metric_history.append(
                            schemas.MLflowMetric(
                                key=metric_file,
                                value=float(parts[0]),
                                timestamp=int(parts[1]),
                                step=int(parts[2]),
                            )
                        )
            metrics[metric_file] = metric_history

    # List artifacts
    artifacts_path = os.path.join(run_path, "artifacts")
    artifacts = []
    if os.path.exists(artifacts_path) and os.path.isdir(artifacts_path):
        for root, dirs, files in os.walk(artifacts_path):
            for name in files:
                full_path = os.path.join(root, name)
                relative_path = os.path.relpath(full_path, artifacts_path)
                artifacts.append(
                    schemas.MLflowArtifact(
                        path=relative_path,
                        is_dir=False,
                        file_size=os.path.getsize(full_path),
                    )
                )
            for name in dirs:
                full_path = os.path.join(root, name)
                relative_path = os.path.relpath(full_path, artifacts_path)
                artifacts.append(
                    schemas.MLflowArtifact(
                        path=relative_path,
                        is_dir=True,
                        file_size=None,
                    )
                )

    return schemas.MLflowRunDetail(
        run_uuid=meta.get("run_uuid"),
        experiment_id=meta.get("experiment_id"),
        run_name=meta.get("run_name"),
        start_time=datetime.datetime.fromtimestamp(meta.get("start_time") / 1000)
        if meta.get("start_time")
        else None,
        end_time=datetime.datetime.fromtimestamp(meta.get("end_time") / 1000)
        if meta.get("end_time")
        else None,
        lifecycle_stage=meta.get("lifecycle_stage"),
        params=params,
        metrics=metrics,
        artifacts=artifacts,
    )
