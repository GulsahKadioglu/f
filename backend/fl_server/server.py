# -*- coding: utf-8 -*-
"""server.py

This file implements the Flower-based federated learning (FL) server with a custom
strategy for secure aggregation using homomorphic encryption. It coordinates the
FL process, aggregates encrypted model updates from clients, and manages the
global model.

Purpose:
- To orchestrate the federated learning process across multiple clients.
- To implement a secure aggregation strategy that protects the privacy of
  individual client model updates.
- To handle the lifecycle of an FL round, including client selection, configuration,
  and model aggregation.
- To persist FL metrics and final model versions to the database.

Key Components:
- `SecureAggregationStrategy`: A custom Flower strategy that extends `FedAsync`
  to handle homomorphically encrypted model parameters.
- `_setup_database`: Initializes the database connection for the server.
- `main`: The main entry point that configures and starts the Flower server.
"""

import json
import os
from collections import OrderedDict

import flwr as fl
import numpy as np
import tenseal as ts
import torch
import yaml

# Use the shared model definition to ensure consistency between client and server
from fl_node.src.model import get_model
from scipy import stats
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend import crud, schemas
from backend.core.config import settings
from backend.db.base_class import Base
from backend.encryption_service import get_context
from backend.models.fl_metrics import FLRoundMetric


def _setup_database():
    """Initializes the database engine and session factory.

    This function sets up the global `engine` and `SessionLocal` variables
    based on the database URL configured in the application settings. It also
    ensures that all tables defined in the SQLAlchemy models are created in the
    database if they don't already exist.
    """
    global engine, SessionLocal
    DATABASE_URL = settings.DATABASE_URL
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)


context = get_context()


class SecureAggregationStrategy(fl.server.strategy.FedAsync):
    """Custom Flower strategy for federated learning with secure aggregation.

    This strategy extends `FedAsync` to handle model weights that are encrypted
    using homomorphic encryption (TenSEAL). It aggregates the encrypted weights
    from clients, decrypts only the final aggregated result, and saves
    performance metrics to the database.

    Attributes:
        num_rounds (int): The total number of federated learning rounds.
        model_name (str): The name of the model architecture being trained.
    """

    def __init__(
        self,
        fraction_fit: float = 1.0,
        fraction_evaluate: float = 1.0,
        min_fit_clients: int = 2,
        min_evaluate_clients: int = 2,
        min_available_clients: int = 2,
        num_rounds: int = 3,
        on_fit_config_fn=None,
        on_evaluate_config_fn=None,
        initial_parameters=None,
        model_name: str = "efficientnet_b4",  # Keep track of the model name
    ):
        """Initializes the secure aggregation strategy.

        Args:
            fraction_fit (float): Fraction of clients to use for training.
            fraction_evaluate (float): Fraction of clients to use for evaluation.
            min_fit_clients (int): Minimum number of clients to be sampled for training.
            min_evaluate_clients (int): Minimum number of clients to be sampled for evaluation.
            min_available_clients (int): Minimum number of clients available before a round starts.
            num_rounds (int): The total number of federated learning rounds.
            on_fit_config_fn (callable, optional): Function to configure training on the client.
            on_evaluate_config_fn (callable, optional): Function to configure evaluation on the client.
            initial_parameters (fl.common.Parameters, optional): The initial global model parameters.
            model_name (str): The name of the model architecture being trained.
        """
        super().__init__(
            fraction_fit=fraction_fit,
            fraction_evaluate=fraction_evaluate,
            min_fit_clients=min_fit_clients,
            min_evaluate_clients=min_evaluate_clients,
            min_available_clients=min_available_clients,
            on_fit_config_fn=on_fit_config_fn,
            on_evaluate_config_fn=on_evaluate_config_fn,
            initial_parameters=initial_parameters,
        )
        self.num_rounds = num_rounds
        self.model_name = model_name

    def detect_outliers(self, results):
        """Detects outliers among client updates based on their loss values.

        Clients with loss values significantly deviating from the mean (based on Z-score)
        are considered outliers and are excluded from aggregation.

        Args:
            results (list[tuple[ClientProxy, FitRes]]): The results from the fit round.

        Returns:
            list[ClientProxy]: A list of client proxies identified as outliers.
        """
        losses = [
            fit_res.metrics["loss"]
            for _, fit_res in results
            if "loss" in fit_res.metrics
        ]
        if len(losses) < 2:  # Not enough data to detect outliers
            return []

        # Calculate Z-scores for loss values
        std_loss = np.std(losses)

        if std_loss == 0:  # Avoid division by zero if all losses are the same
            return []

        z_scores = np.abs(stats.zscore(losses))

        # Define a threshold for outlier detection (e.g., 2.5 standard deviations)
        threshold = 2.5
        outlier_indices = [i for i, z in enumerate(z_scores) if z > threshold]

        if outlier_indices:
            print(
                f"Detected {len(outlier_indices)} outlier(s) based on loss Z-score > {threshold}."
            )
            return [
                results[i][0] for i in outlier_indices
            ]  # Return client proxies of outliers
        return []

    def configure_fit(
        self,
        server_round: int,
        parameters: fl.common.Parameters,
        client_manager: fl.server.client_manager.ClientManager,
    ):
        """Configure the next round of training.

        This method is called by Flower to set up the training round. It defines
        the configuration that will be sent to each client (e.g., number of epochs)
        and samples the clients that will participate in the round.

        Args:
            server_round (int): The current round of federated learning.
            parameters (fl.common.Parameters): The current global model parameters.
            client_manager (fl.server.client_manager.ClientManager): The client manager.

        Returns:
            list[tuple[ClientProxy, FitIns]]: A list of client-configuration pairs.
        """
        config = {"epochs": 3}  # Example: Train for 3 local epochs
        fit_ins = fl.common.FitIns(parameters, config)

        # Sample clients
        sample_size, min_num_clients = self.num_fit_clients(
            client_manager.num_available()
        )
        clients = client_manager.sample(
            num_clients=sample_size, min_num_clients=min_num_clients
        )

        # Return client/config pairs
        return [(client, fit_ins) for client in clients]

    def aggregate_fit(self, server_round, results, failures):
        """Aggregates encrypted model weights from clients.

        This method performs the core secure aggregation logic:
        1. Receives encrypted model parameters from multiple clients.
        2. Sums up the encrypted parameters without decrypting them.
        3. Averages the sum by dividing by the number of clients.
        4. Decrypts only the final, averaged parameters.
        5. In the final round, saves the model state and records it in the database.

        Args:
            server_round (int): The current round of federated learning.
            results (list[tuple[ClientProxy, FitRes]]): A list of results from clients that
                participated in the fit round.
            failures (list[BaseException]): A list of exceptions that occurred on the clients.

        Returns:
            tuple[Parameters, dict]: The aggregated model parameters and an empty metrics dictionary.

        """
        if not results:
            print(
                f"Round {server_round}: No results from clients. Skipping aggregation."
            )
            return None, {}

        if failures:
            print(f"Round {server_round}: Client failures: {failures}")
            for client_proxy, fit_res in results:
                if client_proxy in [f.client_proxy for f in failures]:
                    print(
                        f"Client {client_proxy.cid} failed with reason: {failures[0].reason}"
                    )

        # Detect outliers and filter them out
        outlier_clients = self.detect_outliers(results)
        filtered_results = []
        for client_proxy, fit_res in results:
            if client_proxy not in outlier_clients:
                filtered_results.append((client_proxy, fit_res))
            else:
                print(
                    f"Excluding client {client_proxy.cid} from aggregation due to outlier detection."
                )

        if not filtered_results:
            print("No valid client results after outlier detection. Returning None.")
            return None, {}

        print(f"Aggregating updates from {len(filtered_results)} clients.")

        total_examples = sum([fit_res.num_examples for _, fit_res in filtered_results])

        first_client_encrypted_weights = [
            ts.ckks_vector_from(context, tensor)
            for tensor in filtered_results[0][1].parameters.tensors
        ]
        first_client_num_examples = filtered_results[0][1].num_examples
        aggregated_weights_encrypted = [
            w * first_client_num_examples for w in first_client_encrypted_weights
        ]

        for i in range(1, len(filtered_results)):
            _, fit_res = filtered_results[i]
            client_encrypted_weights = [
                ts.ckks_vector_from(context, tensor)
                for tensor in fit_res.parameters.tensors
            ]
            client_num_examples = fit_res.num_examples

            for j in range(len(aggregated_weights_encrypted)):
                aggregated_weights_encrypted[j] += (
                    client_encrypted_weights[j] * client_num_examples
                )

        aggregated_weights_encrypted = [
            w / total_examples for w in aggregated_weights_encrypted
        ]

        aggregated_ndarrays = [
            np.array(w.decrypt()) for w in aggregated_weights_encrypted
        ]

        if server_round == self.num_rounds:
            print(f"Final round ({server_round}), saving model weights...")
            avg_accuracy = 0.0
            avg_loss = 0.0
            try:
                net = get_model(
                    model_name=self.model_name, num_classes=2, pretrained=False
                )
                params_dict = zip(net.state_dict().keys(), aggregated_ndarrays)
                state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})

                save_dir = os.path.join(os.path.dirname(__file__), "model_versions")
                os.makedirs(save_dir, exist_ok=True)
                file_name = f"model_round_{server_round}.pth"
                save_path = os.path.join(save_dir, file_name)
                torch.save(state_dict, save_path)
                print(f"Model weights successfully saved to '{save_path}'.")

                dvc_metrics_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                    "fl-node",
                    "dvc_global_metrics.json",
                )
                dvc_params_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                    "fl-node",
                    "dvc_global_params.yaml",
                )

                global_metrics = {
                    "global_accuracy": avg_accuracy,
                    "global_loss": avg_loss,
                    "round_number": server_round,
                }
                with open(dvc_metrics_path, "w") as f:
                    json.dump(global_metrics, f, indent=4)
                print(f"Global metrics saved to {dvc_metrics_path}")

                global_params = {
                    "num_rounds": self.num_rounds,
                    "fraction_fit": self.fraction_fit,
                    "min_fit_clients": self.min_fit_clients,
                    "min_available_clients": self.min_available_clients,
                }
                with open(dvc_params_path, "w") as f:
                    yaml.dump(global_params, f, default_flow_style=False)
                print(f"Global parameters saved to {dvc_params_path}")

                db = SessionLocal()
                try:
                    avg_accuracy = 0.0
                    avg_loss = 0.0
                    last_metric = (
                        db.query(FLRoundMetric)
                        .filter(FLRoundMetric.round_number == server_round)
                        .first()
                    )
                    if last_metric:
                        avg_accuracy = last_metric.avg_accuracy
                        avg_loss = last_metric.avg_loss

                    model_version_create = schemas.ModelVersionCreate(
                        version_number=server_round,
                        avg_accuracy=avg_accuracy,
                        avg_loss=avg_loss,
                        description=f"Model trained at the end of FL Round {server_round}.",
                        file_path=save_path,
                    )
                    crud.model_version.create(db, obj_in=model_version_create)
                    print(f"Model version {server_round} saved to the database.")
                except Exception as e:
                    print(f"Error saving model version to the database: {e}")
                    db.rollback()
                finally:
                    db.close()

            except Exception as e:
                print(f"An error occurred while saving the model: {e}")

        parameters_aggregated = fl.common.ndarrays_to_parameters(aggregated_ndarrays)
        return parameters_aggregated, {}

    def aggregate_evaluate(self, server_round, results, failures):
        """Aggregates evaluation results and saves metrics to the database.

        This method is called by Flower after the evaluation round. It aggregates
        the evaluation metrics (like loss and accuracy) from the clients and saves
        the averaged results to the `FLRoundMetric` table in the database.

        Args:
            server_round (int): The current round of federated learning.
            results (list[tuple[ClientProxy, EvaluateRes]]): Results from clients.
            failures (list[BaseException]): Exceptions from clients.

        Returns:
            tuple[float, dict]: The aggregated loss and metrics.

        """
        aggregated_loss, aggregated_metrics = super().aggregate_evaluate(
            server_round, results, failures
        )

        db = SessionLocal()
        try:
            accuracy = aggregated_metrics.get("accuracy")
            fl_metric = FLRoundMetric(
                round_number=server_round,
                avg_accuracy=accuracy,
                avg_loss=aggregated_loss,
                num_clients=len(results),
            )
            db.add(fl_metric)
            db.commit()
            print(f"FL Round {server_round} metrics saved: Accuracy={accuracy}")
        except Exception as e:
            print(f"Error saving FL metrics: {e}")
            db.rollback()
        finally:
            db.close()

        return aggregated_loss, aggregated_metrics


def main():
    """Initializes and starts the federated learning server.

    This function performs the following steps:
    1. Sets up the database connection.
    2. Initializes the global model and its parameters.
    3. Configures the `SecureAggregationStrategy` with the initial parameters
       and other FL settings.
    4. Starts the Flower server, which will then wait for clients to connect
       and begin the federated learning process.
    """
    _setup_database()

    # Define the model to be used for the entire FL session
    model_name_for_session = "vit_small_patch16_224"
    print(f"Initializing server with model: {model_name_for_session}")
    net = get_model(model_name=model_name_for_session, num_classes=2, pretrained=False)
    initial_parameters = fl.common.ndarrays_to_parameters(
        [val.cpu().numpy() for _, val in net.state_dict().items()]
    )

    num_rounds = 3
    strategy = SecureAggregationStrategy(
        min_fit_clients=1,
        min_available_clients=1,
        num_rounds=num_rounds,
        initial_parameters=initial_parameters,
        model_name=model_name_for_session,
    )

    print("Starting Flower server with decryption capabilities...")
    fl.server.start_server(
        server_address="0.0.0.0:8080",
        config=fl.server.ServerConfig(num_rounds=num_rounds),
        strategy=strategy,
    )


if __name__ == "__main__":
    main()
