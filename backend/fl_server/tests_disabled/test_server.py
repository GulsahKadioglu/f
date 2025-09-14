from unittest.mock import MagicMock, patch

import backend.fl_server.server as server
import numpy as np
import pytest

# sys.path.append ve os.path.abspath kullanmadan doğrudan import etmeye çalış
# Eğer bu testler backend/fl_server/tests içinde çalıştırılıyorsa,
# app ve fl_node modüllerine erişim için PYTHONPATH ayarı gerekebilir.
# Ancak, pytest'i proje kökünden çalıştırırken bu sorun çözülmeli.
# Test edilecek modülü import et
from backend.fl_server.server import SecureAggregationStrategy, main
from flwr.common import EvaluateRes, FitRes, Parameters
from flwr.server.strategy import FedAvg


@pytest.fixture(autouse=True)
def mock_db_setup():
    with patch("backend.fl_server.server.create_engine") as mock_create_engine:
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        with patch("backend.fl_server.server.Base.metadata.create_all"):
            yield


# Mock nesneleri
class MockFLRoundMetric:
    def __init__(self, round_number, avg_accuracy, avg_loss, num_clients):
        self.round_number = round_number
        self.avg_accuracy = avg_accuracy
        self.avg_loss = avg_loss
        self.num_clients = num_clients


@pytest.fixture
def mock_crud():
    with patch("backend.fl_server.server.crud") as mock_crud_module:
        yield mock_crud_module


@pytest.fixture
def mock_get_model():
    with patch("backend.fl_server.server.get_model") as mock_get_model_func:
        mock_model = MagicMock()
        mock_model.state_dict.return_value = {
            "layer1.weight": MagicMock(),
            "layer1.bias": MagicMock(),
        }
        mock_get_model_func.return_value = mock_model
        yield mock_get_model_func


@pytest.fixture
def mock_tenseal_context():
    with patch("backend.fl_server.server.get_context") as mock_get_context:
        mock_context = MagicMock()
        mock_get_context.return_value = mock_context
        yield mock_context


def weighted_average(metrics):
    """Computes a weighted average of metrics."""
    accuracies = [num_examples * m["accuracy"] for num_examples, m in metrics]
    examples = [num_examples for num_examples, _ in metrics]
    return {"accuracy": sum(accuracies) / sum(examples)}


@pytest.fixture
def secure_aggregation_strategy(mock_tenseal_context):
    # num_rounds parametresini ekle
    return SecureAggregationStrategy(
        fraction_fit=0.5,
        min_fit_clients=1,
        min_available_clients=1,
        num_rounds=3,
        evaluate_metrics_aggregation_fn=weighted_average,
    )


# Testler
def test_strategy_initialization(secure_aggregation_strategy):
    assert isinstance(secure_aggregation_strategy, FedAvg)
    assert secure_aggregation_strategy.num_rounds == 3


def test_detect_outliers(secure_aggregation_strategy):
    # Scenario 1: No outliers
    results_no_outliers = [
        (MagicMock(cid="client1"), MagicMock(metrics={"loss": 0.1})),
        (MagicMock(cid="client2"), MagicMock(metrics={"loss": 0.15})),
        (MagicMock(cid="client3"), MagicMock(metrics={"loss": 0.12})),
    ]
    outliers = secure_aggregation_strategy.detect_outliers(results_no_outliers)
    assert len(outliers) == 0

    # Scenario 2: One clear outlier
    results_one_outlier = [
        (MagicMock(cid="client1"), MagicMock(metrics={"loss": 0.1})),
        (MagicMock(cid="client2"), MagicMock(metrics={"loss": 10.0})),  # Outlier
        (MagicMock(cid="client3"), MagicMock(metrics={"loss": 0.12})),
    ]
    outliers = secure_aggregation_strategy.detect_outliers(results_one_outlier)
    assert len(outliers) == 1
    assert outliers[0].cid == "client2"

    # Scenario 3: Multiple outliers
    results_multiple_outliers = [
        (MagicMock(cid="client1"), MagicMock(metrics={"loss": 0.1})),
        (MagicMock(cid="client2"), MagicMock(metrics={"loss": 10.0})),  # Outlier
        (MagicMock(cid="client3"), MagicMock(metrics={"loss": 0.12})),
        (MagicMock(cid="client4"), MagicMock(metrics={"loss": 11.0})),  # Outlier
    ]
    outliers = secure_aggregation_strategy.detect_outliers(results_multiple_outliers)
    assert len(outliers) == 2
    assert set([c.cid for c in outliers]) == set(["client2", "client4"])

    # Scenario 4: Empty results
    outliers = secure_aggregation_strategy.detect_outliers([])
    assert len(outliers) == 0

    # Scenario 5: Results without loss metric
    results_no_loss = [
        (MagicMock(cid="client1"), MagicMock(metrics={})),
        (MagicMock(cid="client2"), MagicMock(metrics={})),
    ]
    outliers = secure_aggregation_strategy.detect_outliers(results_no_loss)
    assert len(outliers) == 0

    # Scenario 6: All losses are the same (no std dev)
    results_same_loss = [
        (MagicMock(cid="client1"), MagicMock(metrics={"loss": 0.5})),
        (MagicMock(cid="client2"), MagicMock(metrics={"loss": 0.5})),
        (MagicMock(cid="client3"), MagicMock(metrics={"loss": 0.5})),
    ]
    outliers = secure_aggregation_strategy.detect_outliers(results_same_loss)
    assert len(outliers) == 0


def test_configure_fit_sets_epochs(secure_aggregation_strategy):
    # Mock client_properties (not used in configure_fit, but required by signature)
    mock_client_properties = MagicMock()

    # Call configure_fit for a specific round
    fit_ins_list = secure_aggregation_strategy.configure_fit(
        server_round=1, client_properties=mock_client_properties
    )

    # Assert that the config contains the expected epochs
    assert len(fit_ins_list) > 0
    for _, fit_ins in fit_ins_list:
        assert "epochs" in fit_ins.config
        assert (
            fit_ins.config["epochs"] == 3
        )  # Expecting 3 epochs as set in the strategy


# aggregate_fit metodunu test et
# Bu test, tenseal ve torch bağımlılıkları nedeniyle karmaşıktır.
# Gerçek şifreleme/deşifreleme mantığını test etmek yerine,
# metodun akışını ve veritabanı etkileşimlerini mock'layarak test edeceğiz.
def test_aggregate_fit_saves_model_and_version(
    secure_aggregation_strategy, mock_session_local, mock_crud, mock_get_model
):
    # Mock FitRes nesneleri oluştur
    mock_parameters = MagicMock(spec=Parameters)
    mock_parameters.tensors = [
        b"encrypted_tensor_1",
        b"encrypted_tensor_2",
    ]  # Şifreli tensörler

    # Normal client
    mock_fit_res_normal = MagicMock(spec=FitRes)
    mock_fit_res_normal.parameters = mock_parameters
    mock_fit_res_normal.num_examples = 10
    mock_fit_res_normal.metrics = {"loss": 0.1}

    # Outlier client
    mock_fit_res_outlier = MagicMock(spec=FitRes)
    mock_fit_res_outlier.parameters = mock_parameters
    mock_fit_res_outlier.num_examples = 5
    mock_fit_res_outlier.metrics = {"loss": 10.0}  # High loss to be an outlier

    results = [
        (MagicMock(cid="client1"), mock_fit_res_normal),
        (
            MagicMock(cid="client2"),
            mock_fit_res_outlier,
        ),  # This client should be filtered out
    ]
    failures = []

    # Mock tenseal.ckks_vector_from ve decrypt metodları
    with patch("backend.fl_server.server.ts.ckks_vector_from") as mock_ckks_vector_from:
        with patch("numpy.array") as mock_np_array:
            with patch("torch.tensor") as mock_torch_tensor:
                with patch("torch.save") as mock_torch_save:
                    with patch("os.makedirs") as mock_makedirs:
                        with patch("os.path.join") as mock_path_join:
                            mock_encrypted_vector = MagicMock()
                            mock_encrypted_vector.decrypt.return_value = np.array(
                                [0.5, 0.5]
                            )  # Deşifre edilmiş değerler
                            mock_ckks_vector_from.return_value = mock_encrypted_vector
                            mock_np_array.return_value = np.array([0.5, 0.5])
                            mock_torch_tensor.side_effect = (
                                lambda x: x
                            )  # torch.tensor çağrısını pas geç
                            mock_path_join.side_effect = lambda *args: "/".join(
                                args
                            )  # os.path.join'i mock'la

                            # Mock the database query for FLRoundMetric
                            mock_query = MagicMock()
                            mock_session_local.query.return_value = mock_query
                            mock_query.filter.return_value.first.return_value = (
                                MockFLRoundMetric(
                                    round_number=1,
                                    avg_accuracy=0.9,
                                    avg_loss=0.1,
                                    num_clients=1,
                                )
                            )

                            # Son turu simüle et
                            secure_aggregation_strategy.num_rounds = (
                                1  # Tek turda bitir
                            )
                            aggregated_parameters, metrics = (
                                secure_aggregation_strategy.aggregate_fit(
                                    1, results, failures
                                )
                            )

                            # Modelin kaydedildiğini doğrula
                            mock_torch_save.assert_called_once()
                            mock_makedirs.assert_called_once()

                            # Model versiyonunun veritabanına kaydedildiğini doğrula
                            mock_crud.model_version.create.assert_called_once()
                            args, kwargs = mock_crud.model_version.create.call_args
                            assert kwargs["obj_in"].version_number == 1

                            assert kwargs["obj_in"].avg_accuracy == 0.9
                            assert kwargs["obj_in"].avg_loss == 0.1

                            # Verify that the aggregated parameters are returned
                            assert aggregated_parameters is not None
                            assert isinstance(aggregated_parameters, Parameters)
                            assert (
                                not metrics
                            )  # metrics should be empty for aggregate_fit


@pytest.fixture
def mock_session_local():
    """Mocks the database session to prevent actual database writes."""
    server._setup_database()  # Veritabanı kurulumunu manuel olarak tetikle
    with patch("backend.fl_server.server.SessionLocal") as mock_session_local_class:
        mock_session = MagicMock()
        mock_session_local_class.return_value = mock_session
        yield mock_session


# aggregate_evaluate metodunu test et
def test_aggregate_evaluate_saves_metrics(
    secure_aggregation_strategy, mock_session_local
):
    # Mock EvaluateRes nesneleri oluştur
    mock_evaluate_res = MagicMock(spec=EvaluateRes)
    mock_evaluate_res.num_examples = 10  # Örnek sayısını ekle
    mock_evaluate_res.loss = 0.1
    mock_evaluate_res.metrics = {"accuracy": 0.9}

    results = [("cid1", mock_evaluate_res)]
    failures = []

    aggregated_loss, aggregated_metrics = (
        secure_aggregation_strategy.aggregate_evaluate(1, results, failures)
    )

    # Metriklerin veritabanına kaydedildiğini doğrula
    mock_session_local.add.assert_called_once()
    mock_session_local.commit.assert_called_once()

    # mock_db_session -> mock_session_local olarak düzeltildi
    added_metric = mock_session_local.add.call_args[0][0]
    assert added_metric.round_number == 1
    assert added_metric.avg_accuracy == 0.9
    assert added_metric.avg_loss == 0.1
    assert added_metric.num_clients == 1

    assert aggregated_loss == 0.1
    assert aggregated_metrics["accuracy"] == 0.9


# main fonksiyonunu test et
@pytest.mark.skip(reason="Requires mocking of fl.server.start_server and complex setup")
def test_main_starts_server(mock_tenseal_context):
    """Test if the main function correctly starts the FL server.
    This test requires complex mocking of fl.server.start_server and setup.
    """
    with patch("backend.fl_server.server.fl.server.start_server") as mock_start_server:
        with patch(
            "backend.fl_server.server.SecureAggregationStrategy"
        ) as MockStrategy:
            # Mock SecureAggregationStrategy'nin bir örneğini döndürmesini sağla
            mock_strategy_instance = MagicMock()
            MockStrategy.return_value = mock_strategy_instance

        main()

        mock_start_server.assert_called_once()
        args, kwargs = mock_start_server.call_args
        assert kwargs["server_address"] == "0.0.0.0:8080"
        assert kwargs["config"].num_rounds == 3
        assert kwargs["strategy"] == mock_strategy_instance
