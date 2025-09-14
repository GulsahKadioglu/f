# -*- coding: utf-8 -*-
"""
client.py

This file implements the Flower client for federated learning with homomorphic encryption.
It defines the client-side logic for participating in a federated learning setup,
including fetching the encryption context from the central server, loading local
model and data, and performing encrypted model training and evaluation.

Purpose:
- To enable secure and private participation of individual nodes (clients) in a
  federated learning process.
- To handle the encryption of local model updates using homomorphic encryption
  before sending them to the server.
- To manage local data loading, model training, and evaluation.

Key Components:
- `get_encryption_context()`: Function to retrieve the public encryption context from the server.
- `EncryptedClient` class: Implements the `flwr.client.NumPyClient` interface,
  providing `get_parameters`, `fit`, and `evaluate` methods.
- Integration with PyTorch for model operations and TenSEAL for encryption.
- Logging for monitoring client operations.
"""

import flwr as fl
import torch
import tenseal as ts
import requests
import logging
import numpy as np
from collections import OrderedDict
import opacus
import mlflow

import os
import sys

from .model import get_model, predict_with_uncertainty
from .data_loader import get_dataloader, split_data

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

APP_API_URL = os.getenv("API_URL", "http://127.0.0.1:8080")

def get_encryption_context():
    """
    Fetches the public homomorphic encryption context from the central server.

    This function attempts to retrieve the serialized public encryption context
    from the FastAPI backend. This context is crucial for the client to encrypt
    its local model updates before sending them to the federated learning server,
    thereby ensuring privacy during the aggregation process.

    Returns:
        tenseal.Context: The TenSEAL public encryption context object if the fetch
                         is successful and the context can be deserialized; otherwise, `None`.

    Raises:
        requests.exceptions.RequestException: If there is an issue connecting to the server
                                            or receiving the context.
    """
    try:
        logging.info("Fetching encryption context from server...")
        r = requests.get(f"{APP_API_URL}/api/v1/fl/context")
        r.raise_for_status()
        context = ts.context_from(r.content)
        logging.info("Encryption context successfully received.")
        return context
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to get encryption context from server: {e}")
        return None

# --- Flower Client Definition (Encrypted) ---
class EncryptedClient(fl.client.NumPyClient):
    """
    Flower client implementation that encrypts model parameters using TenSEAL.

    This client participates in federated learning rounds by providing its
    local model parameters, training on local data, and evaluating the global
    model. All parameter exchanges are performed using homomorphic encryption
    to preserve privacy. It extends `flwr.client.NumPyClient` to integrate
    with the Flower federated learning framework.

    Attributes:
        net (torch.nn.Module): The local PyTorch model instance.
        trainloader (torch.utils.data.DataLoader): DataLoader for the local training dataset.
        valloader (torch.utils.data.DataLoader): DataLoader for the local validation dataset.
        public_context (tenseal.Context): The public homomorphic encryption context.
        device (torch.device): The device (CPU or GPU) on which the model operations are performed.
    """
    def __init__(self, cid, net, trainloader, valloader, public_context):
        self.cid = cid
        self.net = net
        self.trainloader = trainloader
        self.valloader = valloader
        self.public_context = public_context
        self.device = torch.device("cpu")

    def get_parameters(self, config):
        """
        Returns the current local model parameters as a list of NumPy arrays.

        This method is called by the Flower framework to retrieve the client's
        current model parameters. These parameters are converted to NumPy arrays and moved
        to CPU memory before being returned.

        Args:
            config (Dict): A dictionary of configuration parameters from the server.
                           Currently not used in this method but required by the Flower API.

        Returns:
            List[np.ndarray]: A list of NumPy arrays, where each array represents
                              a parameter tensor from the model's state dictionary.
        """
        return [val.cpu().numpy() for _, val in self.net.state_dict().items()]

    def fit(self, parameters, config):
        """
        Trains the model on the local dataset using the provided global parameters.

        This method is called by the Flower framework to instruct the client to
        perform a local training step. It loads the global model parameters,
        trains the model on its local training data, and then encrypts and
        serializes the updated model parameters using homomorphic encryption
        before returning them to the server.

        Args:
            parameters (List[np.ndarray]): The global model parameters received from the server.
                                           These are NumPy arrays representing the model weights.
            config (Dict[str, str]): Configuration parameters from the server, such as
                                     the number of local epochs or learning rate.

        Returns:
            Tuple[fl.common.Parameters, int, Dict]:
                - `fl.common.Parameters`: The encrypted and serialized updated model parameters.
                                          The `tensor_type` is set to "encrypted_ckks".
                - `int`: The number of examples used for training (length of the training dataset).
                - `Dict`: A dictionary of metrics from the local training round (currently empty).

        Raises:
            Exception: Catches and logs any errors that occur during the training process,
                       returning a default response with an error message.
        """
        with mlflow.start_run(run_name=f"FL_Client_Round_{config.get('server_round', 'unknown')}"):
            try:
                logging.info(f"Client {self.cid} - Starting fit round {config.get('server_round', 'unknown')}")
                logging.info("Loading global parameters into local model...")
                state_dict = OrderedDict({k: torch.tensor(v) for k, v in zip(self.net.state_dict().keys(), parameters)})
                self.net.load_state_dict(state_dict, strict=True)
                logging.info("Global parameters loaded.")

                optimizer = torch.optim.SGD(self.net.parameters(), lr=0.001)
                criterion = torch.nn.CrossEntropyLoss()

                mlflow.log_param("learning_rate", 0.001)
                epochs = int(config.get("epochs", 1))
                mlflow.log_param("epochs", epochs)
                mlflow.log_param("batch_size", len(self.trainloader.dataset) // len(self.trainloader))

                dp_epsilon = 1.0
                dp_delta = 1e-5
                dp_max_grad_norm = 1.0

                mlflow.log_param("dp_epsilon", dp_epsilon)
                mlflow.log_param("dp_delta", dp_delta)
                mlflow.log_param("dp_max_grad_norm", dp_max_grad_norm)

                print(f"self.net: {self.net}")
                print(f"optimizer: {optimizer}")
                print(f"self.trainloader: {self.trainloader}")
                print(f"dp_epsilon: {dp_epsilon}")
                print(f"dp_delta: {dp_delta}")
                print(f"self.trainloader.batch_size: {self.trainloader.batch_size}")
                print(f"len(self.trainloader.dataset): {len(self.trainloader.dataset)}")
                print(f"epochs: {epochs}")
                privacy_engine = opacus.PrivacyEngine()
                self.net, optimizer, self.trainloader = privacy_engine.make_private(
                    module=self.net,
                    optimizer=optimizer,
                    data_loader=self.trainloader,
                    noise_multiplier=privacy_engine.get_noise_multiplier(target_epsilon=dp_epsilon, target_delta=dp_delta, sample_rate=self.trainloader.batch_size/len(self.trainloader.dataset), epochs=epochs),
                    max_grad_norm=dp_max_grad_norm,
                )
                logging.info("Opacus PrivacyEngine initialized for Differential Privacy.")

                logging.info(f"Starting local training for {epochs} epochs.")
                for epoch in range(epochs):
                    for batch_idx, batch in enumerate(self.trainloader):
                        # --- Modified: Unpack multi-modal data ---
                        images = batch["image"].to(self.device)
                        structured_data = batch["structured_data"].to(self.device) # New
                        labels = batch["label"].to(self.device)

                        optimizer.zero_grad()
                        # --- Modified: Pass multi-modal data to model ---
                        loss = criterion(self.net(images, structured_data), labels) # Pass both
                        loss.backward()
                        optimizer.step()
                        if batch_idx % 10 == 0:
                            logging.info(f"Epoch {epoch+1}/{epochs}, Batch {batch_idx}/{len(self.trainloader)}, Loss: {loss.item():.4f}")
                logging.info("Model training completed.")

                mlflow.log_metric("train_loss", loss.item())

                if privacy_engine.accountant is not None:
                    epsilon_achieved = privacy_engine.accountant.get_epsilon(delta=dp_delta)
                    mlflow.log_metric("epsilon_achieved", epsilon_achieved)
                    logging.info(f"Achieved epsilon for DP: {epsilon_achieved:.2f}")

                logging.info("Encrypting and serializing weights...")
                encrypted_weights = [ts.ckks_vector(self.public_context, val.cpu().numpy().flatten()).serialize() for val in self.net.state_dict().values()]
                
                # mlflow.pytorch.log_model(self.net, "model", registered_model_name="FLClientModel")

                return fl.common.Parameters(tensors=encrypted_weights, tensor_type="encrypted_ckks"), len(self.trainloader.dataset), {}
            except Exception as e:
                import traceback
                traceback.print_exc()
                logging.error(f"An error occurred during training: {e}")
                return self.get_parameters({}), 0, {"error": str(e)}
            

    def evaluate(self, parameters, config):
        """
        Evaluates the global model on the local validation dataset.

        This method is called by the Flower framework to instruct the client to
        evaluate the current global model. It loads the global model parameters,
        evaluates the model's performance (loss and accuracy) on its local
        validation data, and returns the results to the server.

        Args:
            parameters (List[np.ndarray]): The global model parameters received from the server.
                                           These are NumPy arrays representing the model weights.
            config (Dict[str, str]): Configuration parameters from the server.

        Returns:
            Tuple[float, int, Dict]:
                - `float`: The total loss of the model on the validation set.
                - `int`: The number of examples used for evaluation (length of the validation dataset).
                - `Dict`: A dictionary of metrics from the local evaluation round (e.g., accuracy).

        Raises:
            Exception: Catches and logs any errors that occur during the evaluation process,
                       returning a default error response.
        """
        try:
            logging.info(f"Client {self.cid} - Starting evaluation round {config.get('server_round', 'unknown')}")
            logging.info("Loading global parameters into local model for evaluation...")
            state_dict = OrderedDict({k: torch.tensor(v) for k, v in zip(self.net.state_dict().keys(), parameters)})
            self.net.load_state_dict(state_dict, strict=True)
            logging.info("Global parameters loaded for evaluation.")

            logging.info("Starting model evaluation with uncertainty estimation...")
            self.net.eval() # Ensure model is in eval mode for standard evaluation
            criterion = torch.nn.CrossEntropyLoss()
            correct, total, loss = 0, 0, 0.0
            
            # New: Variables to store uncertainty metrics
            all_uncertainties = []
            all_mean_predictions = []

            with torch.no_grad():
                for batch in self.valloader:
                    images = batch["image"].to(self.device)
                    structured_data = batch["structured_data"].to(self.device) # New
                    labels = batch["label"].to(self.device)
                    
                    # --- Modified: Use predict_with_uncertainty for evaluation ---
                    # Assuming get_model was called with enable_mc_dropout=True
                    mean_outputs, uncertainties = predict_with_uncertainty(self.net, images, num_samples=10) # num_samples can be configured

                    # Standard loss calculation using mean_outputs
                    loss += criterion(mean_outputs, labels).item()
                    _, predicted = torch.max(mean_outputs.data, 1)
                    total += labels.size(0)
                    correct += (predicted == labels).sum().item()

                    all_uncertainties.append(uncertainties.cpu().numpy())
                    all_mean_predictions.append(mean_outputs.cpu().numpy())
            
            accuracy = correct / total if total > 0 else 0
            logging.info(f"Evaluation completed: Accuracy={accuracy:.4f}, Loss={loss:.4f}")

            # Aggregate uncertainty metrics
            avg_uncertainty = torch.tensor(np.array(all_uncertainties)).mean().item() # Example: average entropy
            # You might want to log other uncertainty statistics (e.g., max, min, distribution)

            mlflow.log_metric("eval_loss", float(loss))
            mlflow.log_metric("eval_accuracy", float(accuracy))
            mlflow.log_metric("eval_avg_uncertainty", float(avg_uncertainty)) # New metric

            return float(loss), total, {"accuracy": float(accuracy), "avg_uncertainty": float(avg_uncertainty)}
        except Exception as e:
            logging.error(f"An error occurred during evaluation: {e}")
            return float('inf'), 0, {"error": str(e)}
        

if __name__ == "__main__":
    public_context = get_encryption_context()
    if not public_context:
        sys.exit("Failed to retrieve public encryption context. Exiting.")

    DEVICE = torch.device("cpu")
    
    # --- Model Selection for Experimentation ---
    # Easily switch between models by changing the model_name string.
    # Current experiment: Vision Transformer (ViT)
    model_to_use = 'vit_small_patch16_224' 
    logging.info(f"Loading model: {model_to_use}")
    net = get_model(model_name=model_to_use, pretrained=False).to(DEVICE)
    # Load self-supervised pre-trained weights
    try:
        net.load_state_dict(torch.load("final_model.pth"))
        logging.info("Loaded self-supervised pre-trained weights from final_model.pth")
    except FileNotFoundError:
        logging.warning("final_model.pth not found. Starting with randomly initialized weights or ImageNet pre-trained if 'pretrained=True' was used.")
    except Exception as e:
        logging.error(f"Error loading self-supervised pre-trained weights: {e}")
    # ------------------------------------------

    trainloader, valloader = split_data(get_dataloader())

    logging.info("Starting Flower client...")
    fl.client.start_numpy_client(
        server_address=f"{APP_API_URL.replace('http://', '').replace('https://', '')}", 
        client=EncryptedClient(cid="client1", net=net, trainloader=trainloader, valloader=valloader, public_context=public_context)
    )
    logging.info("Flower client stopped.")
