# -*- coding: utf-8 -*-
"""
model.py

This file defines the neural network models used in the federated learning
client. It includes a multi-modal architecture that processes both image and
tabular data, as well as functions for model creation and uncertainty estimation
using Monte Carlo Dropout.

Purpose:
- To define the core deep learning models for the cancer screening task.
- To provide a flexible factory function (`get_model`) for instantiating
  different model architectures.
- To implement a multi-modal network (`MultiModalNet`) capable of fusing
  features from both medical images and structured clinical data.
- To offer a mechanism for estimating model uncertainty (`predict_with_uncertainty`)
  which is crucial for clinical decision support.

Key Components:
- `MultiModalNet`: A PyTorch module that combines a pre-trained image encoder
  (from `timm`) with a simple MLP for tabular data.
- `get_model`: A factory function to create and configure models, including
  the option to enable Monte Carlo Dropout.
- `predict_with_uncertainty`: A function that performs multiple forward passes
  with dropout enabled to generate a distribution of predictions, from which
  uncertainty can be quantified.
"""

import timm
import torch
import torch.nn as nn
import torch.nn.functional as F


class MultiModalNet(nn.Module):
    """
    A multi-modal neural network that processes both images and tabular data.

    This network uses a pre-trained vision model (e.g., ViT) as an image encoder
    and a simple Multi-Layer Perceptron (MLP) as a tabular data encoder. The
    features from both modalities are concatenated and passed through a fusion
    layer before making a final classification.

    Attributes:
        image_encoder (nn.Module): The model for extracting features from images.
        tabular_encoder (nn.Module): The MLP for processing structured data.
        fusion_layer (nn.Module): The layer that combines features from both modalities.
        classifier (nn.Module): The final output layer for classification.
    """

    def __init__(
        self,
        image_model_name: str = "vit_small_patch16_224",
        num_image_features: int = 768,  # Example for vit_small_patch16_224
        tabular_input_dim: int = 10,  # Placeholder: dimension of your structured data
        num_classes: int = 2,
        pretrained_image_model: bool = True,
    ):
        """
        Initializes the MultiModalNet.

        Args:
            image_model_name (str): The name of the pre-trained image model to load
                                    from the `timm` library.
            num_image_features (int): The number of output features from the image
                                      encoder. (This is often auto-detected).
            tabular_input_dim (int): The number of features in the input tabular data.
            num_classes (int): The number of output classes for the classification task.
            pretrained_image_model (bool): Whether to load pre-trained weights for the
                                           image model.
        """
        super().__init__()

        # Image Encoder
        self.image_encoder = timm.create_model(
            image_model_name, pretrained=pretrained_image_model, num_classes=0
        )  # Remove the classifier head
        # Adjust for ViT's feature extractor output if needed
        if "vit" in image_model_name:
            self.image_feature_dim = self.image_encoder.head.in_features
        else:
            self.image_feature_dim = self.image_encoder.num_features

        # Tabular Encoder (simple MLP)
        self.tabular_encoder = nn.Sequential(
            nn.Linear(tabular_input_dim, 64),  # Example hidden layer
            nn.ReLU(),
            nn.Linear(64, 32),  # Output dimension for tabular features
        )
        self.tabular_feature_dim = 32  # Output dimension of tabular_encoder

        # Fusion Layer
        # Concatenate image and tabular features
        self.fusion_layer = nn.Sequential(
            nn.Linear(
                self.image_feature_dim + self.tabular_feature_dim, 128
            ),  # Example fusion layer
            nn.ReLU(),
        )
        self.fused_feature_dim = 128

        # Classifier Head
        self.classifier = nn.Linear(self.fused_feature_dim, num_classes)

    def forward(self, image_input, tabular_input):
        """
        Defines the forward pass for the multi-modal network.

        Args:
            image_input (torch.Tensor): The input tensor for the image modality.
            tabular_input (torch.Tensor): The input tensor for the tabular modality.

        Returns:
            torch.Tensor: The raw output logits from the classifier.
        """
        # Process image
        image_features = self.image_encoder(image_input)

        # Process tabular data
        tabular_features = self.tabular_encoder(tabular_input)

        # Concatenate and fuse features
        fused_features = torch.cat((image_features, tabular_features), dim=1)
        fused_features = self.fusion_layer(fused_features)

        # Classify
        output = self.classifier(fused_features)
        return output


def get_model(
    model_name: str = "multimodal_net",
    num_classes: int = 2,
    pretrained: bool = True,
    tabular_input_dim: int = 10,
    enable_mc_dropout: bool = False,
    mc_dropout_rate: float = 0.5,
):
    """
    Factory function to load or create a specified model.

    This function acts as a model loader. It can instantiate the custom
    `MultiModalNet` or load any standard image classification model from the
    `timm` library. It also provides an option to enable Monte Carlo Dropout
    by adding a dropout layer before the final classifier.

    Args:
        model_name (str): The identifier for the model to load. Use 'multimodal_net'
                          for the custom multi-modal model.
        num_classes (int): The number of output classes.
        pretrained (bool): Whether to use pre-trained weights (for `timm` models or
                           the image encoder in `MultiModalNet`).
        tabular_input_dim (int): The input dimension for the tabular data, required
                                 if `model_name` is 'multimodal_net'.
        enable_mc_dropout (bool): If True, adds a dropout layer to the model's
                                  classifier for uncertainty estimation.
        mc_dropout_rate (float): The dropout probability to use if `enable_mc_dropout`
                                 is True.

    Returns:
        nn.Module: The instantiated PyTorch model.
    """
    if model_name == "multimodal_net":
        model = MultiModalNet(
            image_model_name="vit_small_patch16_224",  # Can be configured
            num_classes=num_classes,
            tabular_input_dim=tabular_input_dim,
            pretrained_image_model=pretrained,
        )
    else:
        # Existing TIMM model loading logic
        model = timm.create_model(
            model_name, pretrained=pretrained, num_classes=num_classes
        )

    if enable_mc_dropout:
        # Add dropout layers or modify existing ones for MC Dropout
        if hasattr(model, "head") and isinstance(model.head, nn.Linear):
            original_head = model.head
            model.head = nn.Sequential(nn.Dropout(p=mc_dropout_rate), original_head)
        elif hasattr(model, "fc") and isinstance(model.fc, nn.Linear):
            original_fc = model.fc
            model.fc = nn.Sequential(nn.Dropout(p=mc_dropout_rate), original_fc)
        else:
            print(
                f"Warning: Could not easily add MC Dropout to model {model_name}. Manual modification might be needed."
            )

    return model


def predict_with_uncertainty(
    model: nn.Module, input_tensor: torch.Tensor, num_samples: int = 10
):
    """
    Performs Monte Carlo Dropout inference to estimate prediction uncertainty.

    This function runs multiple forward passes (`num_samples`) with dropout layers
    activated in training mode. The variation in the resulting predictions is used
    to calculate an uncertainty score, in this case, the predictive entropy.

    Args:
        model (nn.Module): The model with dropout layers enabled for inference.
        input_tensor (torch.Tensor): The input data (e.g., an image batch).
        num_samples (int): The number of forward passes to perform for MC Dropout.

    Returns:
        Tuple[torch.Tensor, torch.Tensor]:
            - mean_predictions (torch.Tensor): The mean of softmax predictions
              across all samples. Shape: (batch_size, num_classes).
            - uncertainty (torch.Tensor): The predictive entropy for each item in
              the batch. Shape: (batch_size,).
    """
    model.train()  # Enable dropout during inference
    predictions = []
    for _ in range(num_samples):
        with torch.no_grad():
            output = model(input_tensor)
            predictions.append(F.softmax(output, dim=1))  # Get probabilities

    predictions_tensor = torch.stack(
        predictions, dim=0
    )  # Shape: (num_samples, batch_size, num_classes)

    mean_predictions = torch.mean(predictions_tensor, dim=0)  # Mean probabilities

    # Calculate uncertainty (e.g., predictive entropy)
    epsilon = 1e-10  # Small value to prevent log(0)
    uncertainty = -torch.sum(
        mean_predictions * torch.log(mean_predictions + epsilon), dim=1
    )

    model.eval()  # Set model back to eval mode
    return mean_predictions, uncertainty
