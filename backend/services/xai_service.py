"""Explainable AI (XAI) service for generating heatmaps.

This file provides functionalities to generate attention heatmaps for a given
model and image, helping to visualize which parts of the input image
the model focuses on for its predictions.
"""

import numpy as np
import torch
from captum.attr import IntegratedGradients
from PIL import Image
from torchvision import transforms


def generate_heatmap(
    model: torch.nn.Module, image_path: str, output_path: str, target_class: int = 0
):
    """Generates an attention heatmap for a given image using a trained model.

    This function uses the Integrated Gradients method from the Captum library
    to compute and visualize the attribution of input features (pixels) to the
    model's prediction. The resulting heatmap indicates the importance of
    different regions in the image for the model's decision-making process.

    Args:
        model (torch.nn.Module): The trained PyTorch model.
        image_path (str): The file path to the input medical image.
        output_path (str): The file path where the generated heatmap image will be saved.
        target_class (int): The target class index for which to generate explanations.
                            Defaults to 0.

    Returns:
        str: The path to the saved heatmap image.

    """
    # 1. Load the image and preprocess it for the model
    img = Image.open(image_path).convert("RGB")
    transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )
    input_tensor = transform(img).unsqueeze(0)  # Add batch dimension
    input_tensor.requires_grad = True

    # 2. Set the model to evaluation mode
    model.eval()

    # 3. Calculate Integrated Gradients using Captum
    ig = IntegratedGradients(model)
    # target=0 or 1, depending on which class you want explanations for
    attr, delta = ig.attribute(
        input_tensor, target=target_class, return_convergence_delta=True
    )
    attr = attr.detach().cpu().numpy()

    # 4. Visualize and save the heatmap
    # Normalize attributions
    attr = np.transpose(attr.squeeze(0), (1, 2, 0))
    heatmap = np.clip(attr.sum(axis=2), 0, np.inf)
    heatmap = (heatmap - np.mean(heatmap)) / np.std(heatmap)
    heatmap = np.clip(heatmap, -1, 1)
    heatmap = (heatmap + 1) / 2
    heatmap = (heatmap * 255).astype(np.uint8)

    heatmap_img = Image.fromarray(heatmap).convert("RGB")
    original_img = Image.open(image_path).convert("RGB").resize(heatmap_img.size)

    # Overlay the heatmap on the original image
    blended_img = Image.blend(original_img, heatmap_img, alpha=0.5)
    blended_img.save(output_path)

    return output_path
