# -*- coding: utf-8 -*-
"""mlflow.py

This file defines the Pydantic schemas for representing MLflow experiment data.
These schemas are used to structure the data retrieved from MLflow's tracking
server or file store, ensuring that the data is validated and can be easily
serialized for API responses.

Purpose:
- To provide clear, validated data structures for MLflow entities like runs,
  parameters, metrics, and artifacts.
- To facilitate the integration of MLflow data into the application's API.

Key Components:
- `MLflowParam`: Schema for a single run parameter.
- `MLflowMetric`: Schema for a single metric entry (including timestamp and step).
- `MLflowArtifact`: Schema for an artifact associated with a run.
- `MLflowRun`: Schema for the basic metadata of a single MLflow run.
- `MLflowRunDetail`: A more detailed schema for a run, including its parameters,
  metrics, and artifacts.
"""

import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel


class MLflowParam(BaseModel):
    """Schema for an MLflow run parameter."""
    key: str
    value: str


class MLflowMetric(BaseModel):
    """Schema for a single MLflow metric data point."""
    key: str
    value: float
    timestamp: int
    step: int


class MLflowArtifact(BaseModel):
    """Schema for an MLflow artifact."""
    path: str
    is_dir: bool
    file_size: Optional[int] = None


class MLflowRun(BaseModel):
    """Schema for the basic metadata of an MLflow run."""
    run_uuid: str
    experiment_id: str
    run_name: Optional[str] = None
    start_time: Optional[datetime.datetime] = None
    end_time: Optional[datetime.datetime] = None
    lifecycle_stage: Optional[str] = None


class MLflowRunDetail(MLflowRun):
    """Detailed schema for an MLflow run, including params, metrics, and artifacts."""
    params: List[MLflowParam]
    metrics: Dict[str, List[MLflowMetric]]
    artifacts: List[MLflowArtifact]
