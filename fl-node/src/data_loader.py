# -*- coding: utf-8 -*-
"""
data_loader.py

This file provides utilities for loading and preprocessing medical image data
for the federated learning client. It handles reading images from a specified
directory structure, applying necessary transformations using MONAI, and
splitting the dataset into training and validation sets.

Purpose:
- To prepare local medical image datasets for training and evaluation within
  the federated learning client.
- To ensure consistent data loading and preprocessing steps across all clients.
- To provide a flexible way to handle different data organizations and apply
  standard image transformations.

Key Components:
- `get_dataloader()`: Function to load images and create a MONAI DataLoader.
- `split_data()`: Function to split a DataLoader's dataset into stratified
  training and validation sets.
- MONAI Transforms: Used for image loading, channel management, intensity scaling,
  and resizing.
- `sklearn.model_selection.train_test_split`: For stratified data splitting.
"""

import os
from glob import glob
import torch
from monai.data import Dataset, DataLoader
from monai.transforms import (
    LoadImaged,
    EnsureChannelFirstd,
    ScaleIntensityRanged,
    Resized,
    Compose
)
from sklearn.model_selection import train_test_split
import pandas as pd
from sklearn.preprocessing import LabelEncoder

# --- New: MultiModalDataset Class ---
class MultiModalDataset(Dataset):
    def __init__(self, image_data_dir: str, structured_data_path: str, transform=None):
        self.image_data_dir = image_data_dir
        self.structured_data_path = structured_data_path
        self.transform = transform

        # Load structured data (e.g., CSV)
        structured_df = pd.read_csv(structured_data_path)
        # Assuming 'patient_id' is a common key to link image and structured data
        structured_df.set_index('patient_id', inplace=True)

        # Encode categorical features
        le = LabelEncoder()
        for col in structured_df.columns:
            if structured_df[col].dtype == 'object':
                structured_df[col] = le.fit_transform(structured_df[col])

        self.structured_df = structured_df


        # Collect image paths and labels (similar to existing logic)
        neg_images = sorted(glob(os.path.join(image_data_dir, "*", "0", "*.png")))
        pos_images = sorted(glob(os.path.join(image_data_dir, "*", "1", "*.png")))

        self.image_paths = neg_images + pos_images
        self.labels = [0] * len(neg_images) + [1] * len(pos_images)

        if not self.image_paths:
            raise ValueError(f"No images found in the data directory: {image_data_dir}")

        # Create a mapping from image_path to patient_id (conceptual)
        # This part needs to be robust based on your actual data organization
        self.data_dicts = []
        for img_path, label in zip(self.image_paths, self.labels):
            # Extract patient_id from image_path (example: /path/to/data_dir/patient_X/0/image.png)
            patient_id = os.path.basename(os.path.dirname(os.path.dirname(img_path)))
            if patient_id in self.structured_df.index:
                self.data_dicts.append({
                    "image": img_path,
                    "label": label,
                    "patient_id": patient_id
                })
            else:
                print(f"Warning: Structured data not found for patient_id: {patient_id} (image: {img_path})")


    def __len__(self):
        return len(self.data_dicts)

    def __getitem__(self, idx):
        data_dict = self.data_dicts[idx]
        image_path = data_dict["image"]
        label = data_dict["label"]
        patient_id = data_dict["patient_id"]

        # Load image
        image_data = LoadImaged(keys=["image"])(data_dict)
        image_tensor = EnsureChannelFirstd(keys=["image"])(image_data)["image"]
        image_tensor = ScaleIntensityRanged(keys=["image"], a_min=0, a_max=255, b_min=0.0, b_max=1.0, clip=True)(
            {"image": image_tensor}
        )["image"]
        image_tensor = Resized(keys=["image"], spatial_size=(224, 224))({"image": image_tensor})["image"]

        # Get structured data
        structured_data = self.structured_df.loc[[patient_id]].values.flatten()
        structured_tensor = torch.tensor(structured_data, dtype=torch.float32)

        return {
            "image": image_tensor,
            "structured_data": structured_tensor,
            "label": label,
            "patient_id": patient_id # Optional, for debugging/tracking
        }

# --- Modified: get_dataloader function ---
def get_dataloader(image_data_dir: str = "/app/data", structured_data_path: str = "/app/structured_data.csv", batch_size: int = 32):
    """
    Reads the dataset from a specified folder structure and creates a MONAI DataLoader.
    Modified to handle multi-modal data (images and structured data).
    """
    transforms = Compose([
        # These transforms are applied within MultiModalDataset's __getitem__
        # LoadImaged, EnsureChannelFirstd, ScaleIntensityRanged, Resized
    ])

    dataset = MultiModalDataset(
        image_data_dir=image_data_dir,
        structured_data_path=structured_data_path,
        transform=transforms # Pass transforms if needed for additional processing
    )
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    return loader

# --- split_data function remains largely the same, but needs to handle multi-modal data in labels extraction ---
def split_data(dataloader: DataLoader, test_size: float = 0.2):
    """
    Splits the given DataLoader's dataset into training and validation DataLoaders.
    Adjusted to handle multi-modal data.
    """
    dataset = dataloader.dataset
    indices = list(range(len(dataset)))

    # Assuming labels are still directly accessible from the dataset's data_dicts
    labels = [item['label'] for item in dataset.data_dicts] # Access data_dicts directly

    train_indices, val_indices = train_test_split(
        indices, test_size=test_size, random_state=42, stratify=labels
    )

    train_subset = torch.utils.data.Subset(dataset, train_indices)
    val_subset = torch.utils.data.Subset(dataset, val_indices)

    train_loader = DataLoader(train_subset, batch_size=dataloader.batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_subset, batch_size=dataloader.batch_size, shuffle=False, num_workers=0)

    return train_loader, val_loader

if __name__ == '__main__':
    # This block is for testing the data loader independently.
    output_file = 'dataloader_test_output.txt'
    with open(output_file, 'w') as f:
        # Redirect print to the file
        original_stdout = __import__('sys').stdout
        __import__('sys').stdout = f

        print("--- Testing DataLoader --- ")
        try:
            # Use relative paths for testing locally
            test_image_dir = '../data'
            test_csv_path = '../data/structured_data.csv'
            
            print(f"Looking for images in: {os.path.abspath(test_image_dir)}")
            print(f"Looking for CSV in: {os.path.abspath(test_csv_path)}")

            # Get the dataloader
            dataloader = get_dataloader(
                image_data_dir=test_image_dir,
                structured_data_path=test_csv_path,
                batch_size=2 # Use a small batch size for testing
            )

            print(f"Successfully created DataLoader. Total samples: {len(dataloader.dataset)}")

            # Get one batch
            first_batch = next(iter(dataloader))
            print("\n--- First Batch Info ---")
            
            # Check the keys
            print(f"Batch keys: {list(first_batch.keys())}")

            # Check the data shapes and types
            image_tensor = first_batch['image']
            structured_tensor = first_batch['structured_data']
            label_tensor = first_batch['label']

            print(f"Image tensor shape: {image_tensor.shape}, type: {image_tensor.dtype}")
            print(f"Structured data tensor shape: {structured_tensor.shape}, type: {structured_tensor.dtype}")
            print(f"Label tensor shape: {label_tensor.shape}, type: {label_tensor.dtype}")
            print("------------------------")
            print("DataLoader test successful!")

        except Exception as e:
            print(f"\nAn error occurred during DataLoader test: {e}")
            import traceback
            traceback.print_exc(file=f)
        finally:
            # Restore stdout
            __import__('sys').stdout = original_stdout
    print(f"Test output written to {output_file}")
