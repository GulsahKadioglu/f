
"""
create_fake_model.py

This script is responsible for creating a dummy or placeholder PyTorch model
and saving its initial weights to a file. This is primarily used for development,
testing, or as a starting point for the federated learning process when a
pre-trained model is not yet available or needed.

Purpose:
- To generate a `final_model.pth` file with initial, untrained model weights.
- To provide a quick way to set up a model file for testing the federated
  learning client or server components without requiring actual training.
- To serve as a placeholder for the global model before the first aggregation round.

Key Components:
- `get_model`: Function imported from `model.py` to define the neural network architecture.
- `torch.save`: PyTorch utility to serialize the model's state dictionary.
- `os.path.join`, `os.path.dirname(__file__)`: Python utilities for constructing file paths.
"""

import torch
from model import get_model
import os

def create_and_save_fake_model():
    """
    Creates a dummy PyTorch model and saves its initial state dictionary (weights).

    This function initializes a model using the `get_model` function, which should
    define the neural network architecture. It then saves the current (untrained)
    state of this model to a file named `final_model.pth` in the same directory
    as this script. This file can then be used by other parts of the application
    that expect a model weights file.

    The `num_classes=2` and `pretrained=False` parameters are chosen to match
    the expected configuration for the federated learning setup.

    Returns:
        None: This function does not return any value but performs a side effect
              of creating a file on the filesystem.
    """
    model = get_model(num_classes=2, pretrained=False)

    save_path = os.path.join(os.path.dirname(__file__), "final_model.pth")

    torch.save(model.state_dict(), save_path)

    print(f"Fake model weights successfully created at '{save_path}'.")

if __name__ == "__main__":
    create_and_save_fake_model()
