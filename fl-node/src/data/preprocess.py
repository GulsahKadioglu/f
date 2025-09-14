# -*- coding: utf-8 -*-
"""preprocess.py

This script provides functionality to preprocess medical images. It reads images
from a structured input directory, converts them to grayscale, and saves them
to a specified output directory while maintaining the original folder structure.

Purpose:
- To perform basic preprocessing on images before they are used for training
  or analysis.
- To provide a simple, command-line-driven tool for image preprocessing.

Usage:
    python preprocess.py <input_base_dir> <output_base_dir>

    - `input_base_dir`: The base directory containing the images, organized by
      patient ID and class label.
    - `output_base_dir`: The base directory where the preprocessed images will be saved.
"""

import os
import sys

from PIL import Image


def preprocess_images(input_base_dir, output_base_dir):
    """Preprocesses images from an input directory and saves them to an output directory.

    This function reads images from a specified `input_base_dir`, where images are
    expected to be organized in folders by patient ID. It converts these images
    to grayscale and saves them to the `output_base_dir`, preserving the same
    folder structure.

    Args:
        input_base_dir (str): The base directory where the images are located.
        output_base_dir (str): The base directory where the preprocessed images
                               will be saved. The directory will be created if it
                               does not exist.

    """
    # Ensure the output directory exists.
    os.makedirs(output_base_dir, exist_ok=True)

    # Scan all 5-digit patient ID folders under the input_base_dir.
    for patient_id_dir in os.listdir(input_base_dir):
        patient_path = os.path.join(input_base_dir, patient_id_dir)
        # Process only 5-digit folders.
        if os.path.isdir(patient_path) and len(patient_id_dir) == 5:
            # Scan for 0 and 1 class folders.
            for class_label in ["0", "1"]:
                class_path = os.path.join(patient_path, class_label)
                if os.path.isdir(class_path):
                    output_class_path = os.path.join(
                        output_base_dir, patient_id_dir, class_label
                    )
                    os.makedirs(output_class_path, exist_ok=True)

                    for img_file in os.listdir(class_path):
                        if img_file.endswith(".png"):
                            img_path = os.path.join(class_path, img_file)
                            try:
                                # Open the image and convert it to grayscale.
                                img = Image.open(img_path).convert("L")
                                # You can add resizing here if needed, for now, we keep the original size.
                                # img = img.resize((50, 50)) # No need for this line if it's already 50x50

                                output_img_path = os.path.join(
                                    output_class_path, img_file
                                )
                                img.save(output_img_path)
                            except Exception as e:
                                print(f"An error occurred with {img_path}: {e}")
    print(f"Preprocessed images have been saved to: {output_base_dir}")


# This block allows the script to be run from the command line.
if __name__ == "__main__":
    # Check if the correct number of command-line arguments are provided.
    if len(sys.argv) != 3:
        print("Usage: python preprocess.py <input_base_dir> <output_base_dir>")
        sys.exit(1)

    # Get the input and output directories from the command-line arguments.
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    # Call the preprocessing function.
    preprocess_images(input_dir, output_dir)