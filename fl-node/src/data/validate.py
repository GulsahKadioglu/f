# -*- coding: utf-8 -*-
"""
This script provides functionality to validate DICOM files based on specific
criteria. It reads all files from an input directory, checks if they are valid
DICOM files with the modality set to 'MG' (Mammography), and writes the paths
of the valid files to an output text file.

Purpose:
- To filter a directory of files, identifying only the valid mammography DICOM images.
- To provide a simple, command-line-driven tool for DICOM validation.

Usage:
    python validate.py <input_path> <output_path>

    - `input_path`: The path to the directory containing the DICOM files to be validated.
    - `output_path`: The path to the text file where the list of valid DICOM file paths
      will be saved.
"""

import os
import sys

import pydicom


def validate_dicom(input_path, output_path):
    """Validates DICOM files in a directory and writes the paths of valid files to an output file.

    This function iterates through all files in the given `input_path`. For each file,
    it attempts to read it as a DICOM file using `pydicom`. A file is considered
    valid if it can be successfully read and its `Modality` attribute is 'MG' (Mammography).
    Any errors or files with an invalid modality are reported to standard error.

    Args:
        input_path (str): The path to the directory containing the DICOM files to validate.
        output_path (str): The path to the text file where the paths of the valid DICOM
                           files will be written, one path per line.

    """
    valid_files = []
    # Iterate over all files in the input directory.
    for filename in os.listdir(input_path):
        filepath = os.path.join(input_path, filename)
        try:
            # Attempt to read the file as a DICOM file.
            ds = pydicom.dcmread(filepath)
            # Check if the DICOM file's Modality is 'MG' (Mammography).
            if ds.Modality == "MG":
                valid_files.append(filepath)
            else:
                # Report files with an invalid modality to stderr.
                print(f"Invalid modality: {filename}", file=sys.stderr)
        except Exception as e:
            # Report any errors encountered while reading the file to stderr.
            print(f"Could not read DICOM file: {filename} - {e}", file=sys.stderr)

    # Write the paths of the valid files to the output file.
    with open(output_path, "w") as f:
        for fpath in valid_files:
            f.write(fpath + "\n")


# This block allows the script to be run from the command line.
if __name__ == "__main__":
    # Check if the correct number of command-line arguments are provided.
    if len(sys.argv) != 3:
        print("Usage: python validate.py <input_path> <output_path>")
        sys.exit(1)

    # Get the input and output paths from the command-line arguments.
    input_dir = sys.argv[1]
    output_file = sys.argv[2]

    # Call the validation function.
    validate_dicom(input_dir, output_file)
