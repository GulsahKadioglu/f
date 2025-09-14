# -*- coding: utf-8 -*-
"""anonymize.py

This script provides functionality to anonymize DICOM files by removing or
replacing sensitive patient information. It reads a list of DICOM file paths
from an input file, processes each file to remove identifying data, and saves
the anonymized files to a specified output directory.

Purpose:
- To protect patient privacy by removing personally identifiable information (PII)
  from DICOM files before they are used for research or training.
- To provide a simple, command-line-driven tool for DICOM anonymization.

Usage:
    python anonymize.py <input_list_path> <output_dir>

    - `input_list_path`: Path to a text file containing one DICOM file path per line.
    - `output_dir`: The directory where the anonymized DICOM files will be saved.
"""

import os
import sys

import pydicom


def anonymize_dicom(input_list_path, output_dir):
    """Anonymizes DICOM files listed in an input file and saves them to an output directory.

    This function iterates through a list of DICOM file paths provided in a text file.
    For each file, it reads the DICOM data, anonymizes sensitive patient fields
    (e.g., PatientName, PatientID, PatientBirthDate) by replacing them with generic
    values or clearing them, and then saves the modified DICOM file to the specified
    output directory.

    Args:
        input_list_path (str): The path to a text file containing a list of DICOM
                               file paths, with one path per line.
        output_dir (str): The path to the directory where the anonymized DICOM files
                          will be saved. The directory will be created if it does not exist.

    """
    # Ensure the output directory exists.
    os.makedirs(output_dir, exist_ok=True)

    # Open the file containing the list of DICOM paths.
    with open(input_list_path, "r") as f:
        # Process each file path in the list.
        for line in f:
            filepath = line.strip()
            try:
                ds = pydicom.dcmread(filepath)

                # Anonymize sensitive fields by replacing them with placeholder values.
                ds.PatientName = "Anonim"
                ds.PatientID = "AnonimID"
                ds.PatientBirthDate = ""
                # Add other sensitive fields to be anonymized here.
                # For example:
                # ds.PatientAddress = ""
                # ds.PatientTelephoneNumbers = ""

                # Construct the output path and save the anonymized file.
                output_filepath = os.path.join(output_dir, os.path.basename(filepath))
                ds.save_as(output_filepath)
            except Exception as e:
                print(f"Error processing file {filepath}: {e}", file=sys.stderr)

    print(f"Anonymized files have been saved to: {output_dir}")


# This block allows the script to be run from the command line.
if __name__ == "__main__":
    # Check if the correct number of command-line arguments are provided.
    if len(sys.argv) != 3:
        print("Usage: python anonymize.py <input_list_path> <output_dir>")
        sys.exit(1)

    # Get the input file path and output directory from the command-line arguments.
    input_path = sys.argv[1]
    output_path = sys.argv[2]

    # Call the anonymization function.
    anonymize_dicom(input_path, output_path)
