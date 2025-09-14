# -*- coding: utf-8 -*-
"""Tests for the MLflow API.

This file contains tests for the MLflow integration endpoints. It uses mocking
to simulate the MLflow file structure and tests the API's ability to correctly
parse and return MLflow run data.

Purpose:
- To verify that the MLflow API endpoints can correctly list runs and retrieve
  run details.
- To ensure that the file parsing logic for MLflow's metadata, parameters,
  metrics, and artifacts is working as expected.
"""

import os
from unittest.mock import mock_open, patch

from fastapi.testclient import TestClient


def test_list_mlflow_runs(client: TestClient, test_admin_token: str):
    """Test listing MLflow runs.

    This test mocks the MLflow file system to simulate the presence of two runs.
    It verifies that the endpoint correctly lists these runs.
    """
    mock_runs = ["run1", "run2"]
    mock_meta_content = """
    run_uuid: run1
    experiment_id: "0"
    run_name: test_run
    start_time: 2023-10-27 10:00:00
    end_time: 2023-10-27 10:10:00
    lifecycle_stage: active
    """

    with patch("os.path.exists", return_value=True):
        with patch("os.listdir", return_value=mock_runs):
            with patch("os.path.isdir", return_value=True):
                with patch("builtins.open", mock_open(read_data=mock_meta_content)):
                    response = client.get(
                        "/api/v1/mlflow/runs",
                        headers={"Authorization": f"Bearer {test_admin_token}"},
                    )
                    assert response.status_code == 200
                    assert len(response.json()) == 2
                    assert response.json()[0]["run_uuid"] == "run1"


def test_get_mlflow_run_detail(client: TestClient, test_admin_token: str):
    """Test getting details for a specific MLflow run.

    This test mocks a complete MLflow run directory structure, including metadata,
    parameters, metrics, and artifacts. It verifies that the endpoint can
    correctly parse all of these components and return them in the expected format.
    """
    mock_run_uuid = "test_run_uuid"
    mock_meta_content = """
run_uuid: test_run_uuid
experiment_id: "0"
run_name: detailed_test_run
start_time: 1678886400000
end_time: 1678887000000
lifecycle_stage: active
"""
    mock_param_content = "param_value"
    mock_metric_content = "1.0 1678886400 0\n2.0 1678886460 1\n"

    # Simplified mock for os.walk to directly provide relative paths
    mock_os_walk_return = [
        ("fl-node/mlruns/0/test_run_uuid/artifacts", ["model"], ["file1.txt"]),
        ("fl-node/mlruns/0/test_run_uuid/artifacts/model", [], ["model.pkl"]),
    ]

    with patch("os.path.exists", return_value=True):
        with patch("os.path.isdir", return_value=True):
            with patch(
                "os.listdir",
                side_effect=lambda path: {
                    os.path.join("fl-node/mlruns/0", mock_run_uuid, "params"): [
                        "param1"
                    ],
                    os.path.join("fl-node/mlruns/0", mock_run_uuid, "metrics"): [
                        "metric1"
                    ],
                }.get(path, []),
            ):
                with patch(
                    "builtins.open",
                    side_effect=lambda path, mode: mock_open(
                        read_data=mock_meta_content
                    )()
                    if "meta.yaml" in path
                    else (
                        mock_open(read_data=mock_param_content)()
                        if "param1" in path
                        else (
                            mock_open(read_data=mock_metric_content)()
                            if "metric1" in path
                            else mock_open()()
                        )
                    ),
                ):
                    with patch("os.walk", return_value=mock_os_walk_return):
                        with patch("os.path.getsize", return_value=100):
                            response = client.get(
                                f"/api/v1/mlflow/runs/{mock_run_uuid}",
                                headers={"Authorization": f"Bearer {test_admin_token}"},
                            )

                            assert response.status_code == 200
                            data = response.json()
                            assert data["run_uuid"] == mock_run_uuid
                            assert data["run_name"] == "detailed_test_run"
                            assert len(data["params"]) == 1
                            assert data["params"][0]["key"] == "param1"
                            assert data["params"][0]["value"] == "param_value"
                            assert "metric1" in data["metrics"]
                            assert len(data["metrics"]["metric1"]) == 2
                            assert data["metrics"]["metric1"][0]["value"] == 1.0
                            assert len(data["artifacts"]) == 3  # 1 dir, 2 files
                            assert data["artifacts"][0]["path"] == "file1.txt"
                            assert data["artifacts"][1]["path"] == "model"
                            assert data["artifacts"][2]["path"] == os.path.join(
                                "model", "model.pkl"
                            )
