# -*- coding: utf-8 -*-
"""test_data_loader.py

This file contains unit tests for the data loading and preprocessing utilities
in `src/data_loader.py`. It uses the `pytest` framework to test the
`MultiModalDataset`, `get_dataloader`, and `split_data` functions.

Purpose:
- To ensure that the data loading and preprocessing pipeline works as expected.
- To verify that the `MultiModalDataset` correctly loads and combines image
  and structured data.
- To test the creation of `DataLoader` instances and the splitting of data
  into training and validation sets.

Key Components:
- `pytest` fixtures: To set up a temporary directory with dummy image and
  structured data for the tests.
- Test functions: To test the initialization, item retrieval, and data loading
  capabilities of the data loader components.
"""

import os
import shutil
import sys
from unittest.mock import Mock, patch

import pandas as pd
import pytest
import torch
from PIL import Image
from torch.utils.data import DataLoader

# Add the project root to the Python path to allow imports from the `src` directory.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from data_loader import MultiModalDataset, get_dataloader, split_data

# Define a temporary directory for test data.
TEST_DATA_DIR = "test_data_loader"

# Define a dummy structured data CSV path.
DUMMY_STRUCTURED_DATA_PATH = os.path.join(TEST_DATA_DIR, "structured_data.csv")


@pytest.fixture(scope="module")
def setup_dummy_data():
    """Fixture to set up a dummy dataset for testing.

    This fixture creates a temporary directory with a dummy folder structure
    for images and a dummy CSV file for structured data. It yields control to
    the test functions and then cleans up the temporary directory after the
    tests are completed.
    """
    # Create dummy image data structure.
    os.makedirs(os.path.join(TEST_DATA_DIR, "patient_001", "0"), exist_ok=True)
    os.makedirs(os.path.join(TEST_DATA_DIR, "patient_002", "1"), exist_ok=True)
    os.makedirs(os.path.join(TEST_DATA_DIR, "patient_003", "0"), exist_ok=True)
    os.makedirs(os.path.join(TEST_DATA_DIR, "patient_004", "1"), exist_ok=True)
    os.makedirs(os.path.join(TEST_DATA_DIR, "patient_005", "0"), exist_ok=True)
    os.makedirs(os.path.join(TEST_DATA_DIR, "patient_006", "1"), exist_ok=True)

    # Create a dummy black image.
    dummy_image = Image.new("L", (10, 10), color=0)
    dummy_image.save(os.path.join(TEST_DATA_DIR, "patient_001", "0", "image1.png"))
    dummy_image.save(os.path.join(TEST_DATA_DIR, "patient_002", "1", "image2.png"))
    dummy_image.save(os.path.join(TEST_DATA_DIR, "patient_003", "0", "image3.png"))
    dummy_image.save(os.path.join(TEST_DATA_DIR, "patient_004", "1", "image4.png"))
    dummy_image.save(os.path.join(TEST_DATA_DIR, "patient_005", "0", "image5.png"))
    dummy_image.save(os.path.join(TEST_DATA_DIR, "patient_006", "1", "image6.png"))

    # Create dummy structured data CSV.
    structured_data = pd.DataFrame(
        {
            "patient_id": [
                "patient_001",
                "patient_002",
                "patient_003",
                "patient_004",
                "patient_005",
                "patient_006",
            ],
            "age": [60, 45, 70, 55, 65, 50],
            "gender": ["Male", "Female", "Male", "Female", "Male", "Female"],
            "bmi": [25.1, 22.5, 30.0, 28.0, 26.0, 24.0],
            "smoking_status": ["Never", "Current", "Former", "Never", "Current", "Former"],
            "family_history": [0, 1, 0, 1, 0, 1],
            "tumor_marker_A": [5.2, 15.8, 7.1, 10.0, 8.0, 12.0],
        }
    )
    structured_data.to_csv(DUMMY_STRUCTURED_DATA_PATH, index=False)

    yield  # Provide the dummy data for tests.

    # Clean up after tests.
    shutil.rmtree(TEST_DATA_DIR)


def test_multimodal_dataset_init(setup_dummy_data):
    """Test the initialization of the `MultiModalDataset`."""
    dataset = MultiModalDataset(
        image_data_dir=TEST_DATA_DIR, structured_data_path=DUMMY_STRUCTURED_DATA_PATH
    )
    assert len(dataset) == 6
    assert len(dataset.data_dicts) == 6


def test_multimodal_dataset_getitem(setup_dummy_data):
    """Test the `__getitem__` method of the `MultiModalDataset`."""
    dataset = MultiModalDataset(
        image_data_dir=TEST_DATA_DIR, structured_data_path=DUMMY_STRUCTURED_DATA_PATH
    )
    item = dataset[0]

    assert "image" in item
    assert "structured_data" in item
    assert "label" in item
    assert "patient_id" in item

    assert isinstance(item["image"], torch.Tensor)
    assert isinstance(item["structured_data"], torch.Tensor)
    assert item["structured_data"].shape[0] == 6  # 6 features in dummy structured data
    assert item["label"] in [0, 1]


def test_get_dataloader(setup_dummy_data):
    """Test the `get_dataloader` function."""
    dataloader = get_dataloader(
        image_data_dir=TEST_DATA_DIR,
        structured_data_path=DUMMY_STRUCTURED_DATA_PATH,
        batch_size=1,
    )
    assert isinstance(dataloader, DataLoader)
    batch = next(iter(dataloader))
    assert "image" in batch
    assert "structured_data" in batch
    assert "label" in batch
    assert batch["image"].shape[0] == 1
    assert batch["structured_data"].shape == (1, 6)  # Batch size 1, 6 features
    assert batch["label"].shape == (1,)


def test_split_data(setup_dummy_data):
    """Test the `split_data` function."""
    dataloader = get_dataloader(
        image_data_dir=TEST_DATA_DIR,
        structured_data_path=DUMMY_STRUCTURED_DATA_PATH,
        batch_size=2,
    )
    train_loader, val_loader = split_data(dataloader, test_size=0.5)

    assert isinstance(train_loader, DataLoader)
    assert isinstance(val_loader, DataLoader)

    # Check if data is split (approximate due to small dataset and stratification).
    total_samples = len(dataloader.dataset)
    assert len(train_loader.dataset) + len(val_loader.dataset) == total_samples

    # Check if batches can be iterated.
    _ = next(iter(train_loader))
    _ = next(iter(val_loader))
