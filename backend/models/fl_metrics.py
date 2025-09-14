"""fl_metrics.py

This file defines the SQLAlchemy ORM model for `FLRoundMetric`.
This model is designed to store performance metrics and other relevant data
for each round of the federated learning (FL) process. Tracking these metrics
is crucial for monitoring the progress and effectiveness of the FL model training.

Purpose:
- To persist federated learning round statistics in the database.
- To enable historical analysis and visualization of FL model performance over time.
- To provide a structured way to record key metrics like accuracy, loss, and client participation.

Key Components:
- `FLRoundMetric` class: Defines the database table structure and column types.
- `Base`: The declarative base class from SQLAlchemy, which all ORM models inherit from.
- SQLAlchemy `Column` types: Specify the data type and constraints for each attribute.
- `func.now()`: Used for automatically setting the `timestamp` to the current time upon record creation.
"""

from sqlalchemy import Column, DateTime, Float, Integer
from sqlalchemy.sql import func

from ..db.base_class import Base


class FLRoundMetric(Base):
    """SQLAlchemy ORM model representing a record of metrics for a single federated learning round.

    This table stores key performance indicators and operational details for each
    completed round of federated learning, allowing for historical tracking and analysis.

    Attributes:
        id (int): The primary key of the `fl_round_metrics` table. It's an auto-incrementing
                  integer, uniquely identifying each metric record.
        round_number (int): The sequential number of the federated learning round.
                            Indexed for faster lookups and ordered retrieval.
                            `nullable=False` ensures this field must always have a value.
        avg_accuracy (float): The average accuracy achieved by the global model at the end
                              of this FL round. `nullable=True` allows for cases where accuracy
                              might not be available or applicable.
        avg_loss (float): The average loss value of the global model at the end of this FL round.
                          `nullable=True` allows for cases where loss might not be available.
        num_clients (int): The number of clients that successfully participated in this specific
                           federated learning round. `nullable=False` ensures this field is always present.
        timestamp (DateTime): The timestamp indicating when this metric record was created.
                              `server_default=func.now()` automatically sets the current database
                              server time upon insertion.

    """

    __tablename__ = "fl_round_metrics"
    id = Column(Integer, primary_key=True, index=True)
    round_number = Column(Integer, index=True, nullable=False)
    avg_accuracy = Column(Float, nullable=True)
    avg_loss = Column(Float, nullable=True)
    num_clients = Column(Integer, nullable=False)
    avg_uncertainty = Column(Float, nullable=True)
    timestamp = Column(DateTime, server_default=func.now())
