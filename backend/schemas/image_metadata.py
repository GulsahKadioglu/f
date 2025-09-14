# -*- coding: utf-8 -*-
"""image_metadata.py

This file defines the Pydantic schema for `ImageMetadata`.
This schema is used for validating and serializing metadata associated with
a medical image, particularly DICOM attributes and storage information.

Purpose:
- To define a structured format for image metadata.
- To ensure type validation for image metadata fields.
- To facilitate the transfer of image metadata between different parts of the application.

Key Components:
- `ImageMetadata`: A Pydantic model representing the metadata of a medical image.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict


class ImageMetadata(BaseModel):
    """Pydantic schema for medical image metadata.

    This schema represents the metadata associated with a medical image, including
    both storage-related information (URL, path) and DICOM-specific attributes.

    Attributes:
        url (str): The accessible URL for the image.
        image_path (str): The internal file path or storage key for the image.
        image_type (Optional[str]): The type or category of the image (e.g., 'CT', 'X-RAY').
        study_instance_uid (str): The DICOM Study Instance UID.
        series_instance_uid (str): The DICOM Series Instance UID.
        sop_instance_uid (str): The DICOM SOP Instance UID.
        modality (str): The DICOM modality (e.g., 'CT', 'MR').
        instance_number (int): The DICOM instance number within a series.
    """
    url: str
    image_path: str
    image_type: Optional[str]
    study_instance_uid: str
    series_instance_uid: str
    sop_instance_uid: str
    modality: str
    instance_number: int

    model_config = ConfigDict(from_attributes=True)
