# -*- coding: utf-8 -*-
"""test_client.py

This file contains unit tests for the Flower client implementation in `src/client.py`.
It uses the `pytest` framework and `unittest.mock` to test the client's
functionalities in isolation, including fetching the encryption context, handling
model parameters, and performing `fit` and `evaluate` operations.

Purpose:
- To ensure the correctness and reliability of the federated learning client.
- To verify that the client interacts correctly with mocked external services
  (e.g., the central server for encryption context).
- To test the client's logic for training, evaluation, and parameter handling.

Key Components:
- `pytest` fixtures: To set up mock objects and test data for the tests.
- `unittest.mock.patch`: To mock external dependencies like `requests`, `tenseal`,
  `torch`, and `opacus`.
- Test functions: To test individual functions and methods of the `EncryptedClient`.
"""

# ruff: noqa: E402
import os
import sys
from collections import OrderedDict
from unittest.mock import MagicMock, patch

import flwr as fl
import numpy as np
import pytest
import requests
import torch

# Add the project root to the Python path to allow imports from the `src` directory.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the module to be tested.
from src.client import EncryptedClient, get_encryption_context


# Mock objects for external dependencies.
class MockContext:
    """A mock class for `tenseal.Context`."""

    def __init__(self):
        self.public_keys = MagicMock()

    def serialize(self, save_public_key, save_secret_key):
        return b"serialized_context"


class MockCKKSVector:
    """A mock class for `tenseal.CKKSVector`."""

    def __init__(self, context, data):
        self.context = context
        self.data = data

    def serialize(self):
        return b"serialized_ckks_vector"

    def decrypt(self):
        return self.data


# Pytest fixtures to set up the test environment.
@pytest.fixture
def mock_requests_get():
    """Fixture to mock `requests.get` calls."""
    with patch("src.client.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.content = b"mock_context_content"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        yield mock_get


@pytest.fixture
def mock_tenseal_context_from():
    """Fixture to mock `tenseal.context_from`."""
    with patch("src.client.ts.context_from") as mock_context_from:
        mock_context_from.return_value = MockContext()
        yield mock_context_from


@pytest.fixture
def mock_get_model():
    """Fixture to mock `get_model` function."""
    with patch("src.client.get_model") as mock_get_model_func:
        mock_model = MagicMock(spec=torch.nn.Module)
        mock_model.state_dict.return_value = OrderedDict(
            {"layer1.weight": torch.tensor([1.0, 2.0]), "layer1.bias": torch.tensor([3.0])}
        )
        mock_model.parameters.return_value = [
            torch.nn.Parameter(torch.randn(2, 2), requires_grad=True)
        ]
        mock_model.return_value = torch.randn(1, 2)
        mock_get_model_func.return_value = mock_model
        yield mock_get_model_func


@pytest.fixture
def mock_get_dataloader():
    """Fixture to mock `get_dataloader` function."""
    with patch("src.client.get_dataloader") as mock_dataloader_func:
        mock_dataloader = MagicMock()
        mock_dataloader.dataset = MagicMock(len=lambda: 10)  # Mock dataset length
        mock_dataloader_func.return_value = mock_dataloader
        yield mock_dataloader_func


@pytest.fixture
def mock_split_data():
    """Fixture to mock `split_data` function."""
    with patch("src.client.split_data") as mock_split_data_func:
        mock_trainloader = MagicMock()
        mock_trainloader.dataset = MagicMock()
        mock_trainloader.dataset.__len__.return_value = 8
        mock_trainloader.__len__.return_value = 2  # Mock len(trainloader)
        mock_trainloader.batch_size = 4  # Mock batch_size
        mock_trainloader.__iter__.return_value = iter(
            [
                {
                    "image": torch.randn(1, 3, 224, 224),
                    "structured_data": torch.randn(1, 6),
                    "label": torch.tensor([0]),
                }
            ]
        )

        mock_valloader = MagicMock()
        mock_valloader.dataset = MagicMock()
        mock_valloader.dataset.__len__.return_value = 2
        mock_valloader.__iter__.return_value = iter(
            [
                {
                    "image": torch.randn(1, 3, 224, 224),
                    "structured_data": torch.randn(1, 6),
                    "label": torch.tensor([0]),
                }
            ]
        )

        mock_split_data_func.return_value = (mock_trainloader, mock_valloader)
        yield mock_split_data_func


@pytest.fixture
def mock_tenseal_ckks_vector():
    """Fixture to mock `tenseal.ckks_vector`."""
    with patch("src.client.ts.ckks_vector") as mock_ckks_vector:
        mock_ckks_vector.return_value = MockCKKSVector(
            None, None
        )  # context and data are not important
        yield mock_ckks_vector


# Test functions for the client.
def test_get_encryption_context_success(mock_requests_get, mock_tenseal_context_from):
    """Test successful retrieval of the encryption context."""
    context = get_encryption_context()
    mock_requests_get.assert_called_once_with(
        "http://127.0.0.1:8080/api/v1/fl/context"
    )
    mock_tenseal_context_from.assert_called_once_with(b"mock_context_content")
    assert isinstance(context, MockContext)


def test_get_encryption_context_failure(mock_requests_get):
    """Test failure to retrieve the encryption context."""
    mock_requests_get.side_effect = requests.exceptions.RequestException("Test Error")
    context = get_encryption_context()
    assert context is None


@pytest.fixture
def encrypted_client(
    mock_get_model, mock_get_dataloader, mock_split_data, mock_tenseal_context_from
):
    """Fixture to create an instance of `EncryptedClient` with mocked dependencies."""
    mock_net = mock_get_model.return_value
    mock_trainloader, mock_valloader = mock_split_data.return_value
    mock_context = mock_tenseal_context_from.return_value
    client = EncryptedClient(
        cid="test_client",
        net=mock_net,
        trainloader=mock_trainloader,
        valloader=mock_valloader,
        public_context=mock_context,
    )
    return client


def test_get_parameters(encrypted_client):
    """Test the `get_parameters` method of `EncryptedClient`."""
    parameters = encrypted_client.get_parameters(config={})
    assert len(parameters) == 2
    assert np.array_equal(parameters[0], np.array([1.0, 2.0]))
    assert np.array_equal(parameters[1], np.array([3.0]))


@pytest.fixture
def mock_opacus_privacy_engine():
    """Fixture to mock `opacus.PrivacyEngine`."""
    with patch("src.client.opacus.PrivacyEngine") as mock_pe_class:
        mock_pe_instance = MagicMock()
        mock_pe_instance.get_noise_multiplier.return_value = 0.1
        mock_pe_class.return_value = mock_pe_instance
        mock_pe_instance.make_private.side_effect = (
            lambda module, optimizer, data_loader, noise_multiplier, max_grad_norm: (
                module,
                optimizer,
                data_loader,
            )
        )
        mock_pe_instance.accountant = MagicMock()
        mock_pe_instance.accountant.get_epsilon.return_value = (
            5.0  # Mock a value for epsilon
        )
        yield mock_pe_class


def test_fit(encrypted_client, mock_tenseal_ckks_vector, mock_opacus_privacy_engine):
    """Test the `fit` method of `EncryptedClient`."""
    # Mock parameters
    parameters = [np.array([0.5, 0.6]), np.array([0.7])]

    # Mock torch.nn.CrossEntropyLoss and torch.optim.SGD
    with patch("src.client.torch.nn.CrossEntropyLoss") as MockLoss:
        with patch("src.client.torch.optim.SGD") as MockSGD:
            with patch("src.client.mlflow.pytorch.log_model") as MockLogModel:
                mock_loss_instance = MagicMock()
                mock_loss_instance.return_value = torch.tensor(0.1, requires_grad=True)
                MockLoss.return_value = mock_loss_instance

                mock_optimizer_instance = MagicMock()
                MockSGD.return_value = mock_optimizer_instance

                # Test with default epochs (1)
                result_parameters, num_examples, metrics = encrypted_client.fit(
                    parameters, config={}
                )

                mock_tenseal_ckks_vector.assert_called()
                assert num_examples == 8
                assert isinstance(result_parameters, fl.common.Parameters)
                assert result_parameters.tensor_type == "encrypted_ckks"


def test_evaluate(encrypted_client):
    """Test the `evaluate` method of `EncryptedClient`."""
    # Mock parameters
    parameters = [np.array([0.5, 0.6]), np.array([0.7])]

    # Mock torch.nn.CrossEntropyLoss
    with patch("src.client.torch.nn.CrossEntropyLoss") as MockLoss:
        mock_loss_instance = MagicMock()
        mock_loss_instance.return_value = torch.tensor(0.1)
        MockLoss.return_value = mock_loss_instance

        loss, num_examples, metrics = encrypted_client.evaluate(parameters, config={})

        assert loss == pytest.approx(0.1)  # Approximate value check
        assert num_examples > 0
        assert "accuracy" in metrics
        assert metrics["accuracy"] >= 0
