# -*- coding: utf-8 -*-
"""predict.py

This script provides a command-line interface for performing inference on a single
medical image using a trained model. It loads a model, preprocesses an image,
and outputs the predicted class and confidence score.

Purpose:
- To provide a simple way to test a trained model on a single image.
- To serve as an example of how to use the model for inference.

Usage:
    python predict.py --model_path <path_to_model.pth> --image_path <path_to_image.png>
"""

import argparse
import os

import torch
from monai.transforms import (
    Compose,
    EnsureChannelFirst,
    LoadImage,
    Resize,
    ScaleIntensityRange,
)

from .model import get_model

# Set the device to CPU.
DEVICE = torch.device("cpu")


def predict(model_path: str, image_path: str):
    """Loads a trained model and performs prediction on a single image.

    This function takes the path to a trained model's weights and an image path,
    loads the model, preprocesses the image using MONAI transforms, and then
    outputs the predicted class and the confidence score for that prediction.

    Args:
        model_path (str): The path to the trained model's weights (.pth file).
        image_path (str): The path to the image file for prediction.

    """
    # Make paths absolute to avoid ambiguity.
    model_path = os.path.abspath(model_path)
    image_path = os.path.abspath(image_path)

    # 1. Load the model.
    print(f"Loading model: {model_path}")
    # We don't use pre-trained weights here; we load our own trained weights.
    model = get_model(num_classes=2, pretrained=False)
    model.load_state_dict(torch.load(model_path, map_location=DEVICE))
    model.to(DEVICE)
    model.eval()  # Set the model to evaluation mode.
    print("Model loaded successfully.")

    # 2. Prepare the image.
    print(f"Processing image: {image_path}")
    # Define the same transforms used during training/validation.
    transforms = Compose(
        [
            LoadImage(image_only=True),
            EnsureChannelFirst(),
            ScaleIntensityRange(a_min=0, a_max=255, b_min=0.0, b_max=1.0, clip=True),
            Resize(spatial_size=(224, 224)),
        ]
    )
    # Apply transforms and add a batch dimension.
    image = transforms(image_path).unsqueeze(0)
    image = image.to(DEVICE)

    # 3. Make prediction.
    print("Making prediction...")
    with torch.no_grad():  # Disable gradient calculation for inference.
        output = model(image)
        # Apply softmax to get probabilities.
        probabilities = torch.nn.functional.softmax(output, dim=1)
        # Get the class with the highest probability.
        predicted_class = torch.argmax(probabilities, dim=1).item()
        # Get the confidence score for the predicted class.
        confidence = probabilities.max().item()

    # 4. Display the result.
    labels = {0: "Healthy", 1: "Cancerous"}
    print("\n--- Prediction Result ---")
    print(f"Predicted Class: {labels[predicted_class]} (Class {predicted_class})")
    print(f"Confidence Score: {confidence:.4f}")
    print("---------------------")


# This block allows the script to be run from the command line.
if __name__ == "__main__":
    # Set up the argument parser.
    parser = argparse.ArgumentParser(
        description="Perform cancer prediction on an image."
    )
    parser.add_argument(
        "--model_path",
        type=str,
        required=True,
        help="Path to the trained model weights (.pth file).",
    )
    parser.add_argument(
        "--image_path",
        type=str,
        required=True,
        help="Path to the image file for prediction.",
    )
    args = parser.parse_args()

    # Call the prediction function with the provided arguments.
    predict(args.model_path, args.image_path)