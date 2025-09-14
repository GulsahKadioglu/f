# -*- coding: utf-8 -*-
"""simple_test.py

This script performs a simple test to ensure that the required libraries
(PyTorch and timm) are installed correctly and that a basic model can be
created without errors. It serves as a quick sanity check for the environment.
"""

import torch
import timm
print("PyTorch and timm imported successfully!")
print("Attempting to create model...")
model = timm.create_model('vit_small_patch16_224', pretrained=False, num_classes=0)
print("Model created successfully!")
