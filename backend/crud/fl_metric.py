"""fl_metric.py

This file provides CRUD (Create, Read, Update, Delete) operations for the
Federated Learning (FL) metrics in the database. It encapsulates the logic
for interacting with the `FLRoundMetric` SQLAlchemy model.

Purpose:
- To abstract database interactions for FL metrics, ensuring clean separation
  of concerns.
- To provide standardized functions for common operations like creating new metrics,
  retrieving existing ones, updating, and deleting them.

Key Components:
- Functions for `create`, `get`, `get_all`, `get_latest`, `get_by_round`,
  `remove`, and `update` operations on `FLRoundMetric` objects.
- Utilizes SQLAlchemy ORM for database queries.
"""

from sqlalchemy.orm import Session

from ..models.fl_metrics import FLRoundMetric
from ..schemas.fl_metric import FLRoundMetricBase, FLRoundMetricUpdate


def create(db: Session, obj_in: FLRoundMetricBase) -> FLRoundMetric:
    """Creates a new FLRoundMetric record in the database.

    Args:
        db (Session): The database session.
        obj_in (FLRoundMetricBase): Pydantic model with the data for the new metric.

    Returns:
        FLRoundMetric: The newly created FLRoundMetric object.

    """
    db_obj = FLRoundMetric(
        round_number=obj_in.round_number,
        avg_accuracy=obj_in.avg_accuracy,
        avg_loss=obj_in.avg_loss,
        num_clients=obj_in.num_clients,
        avg_uncertainty=obj_in.avg_uncertainty,  # New
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get(db: Session, id: int) -> FLRoundMetric | None:
    """Retrieves an FLRoundMetric record by its ID.

    Args:
        db (Session): The database session.
        id (int): The ID of the FLRoundMetric to retrieve.

    Returns:
        FLRoundMetric | None: The FLRoundMetric object if found, else None.

    """
    return db.query(FLRoundMetric).filter(FLRoundMetric.id == id).first()


def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[FLRoundMetric]:
    """Retrieves a list of FLRoundMetric records with pagination.

    Args:
        db (Session): The database session.
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to retrieve.

    Returns:
        list[FLRoundMetric]: A list of FLRoundMetric objects.

    """
    return db.query(FLRoundMetric).offset(skip).limit(limit).all()


def get_latest(db: Session) -> FLRoundMetric | None:
    """Retrieves the latest FLRoundMetric record based on timestamp.

    Args:
        db (Session): The database session.

    Returns:
        FLRoundMetric | None: The latest FLRoundMetric object if found, else None.

    """
    return db.query(FLRoundMetric).order_by(FLRoundMetric.round_number.desc()).first()


def get_by_round(db: Session, round_num: int) -> FLRoundMetric | None:
    """Retrieves an FLRoundMetric record by its round number.

    Args:
        db (Session): The database session.
        round_num (int): The round number of the FLRoundMetric to retrieve.

    Returns:
        FLRoundMetric | None: The FLRoundMetric object if found, else None.

    """
    return (
        db.query(FLRoundMetric).filter(FLRoundMetric.round_number == round_num).first()
    )


def remove(db: Session, id: int) -> FLRoundMetric | None:
    """Removes an FLRoundMetric record by its ID.

    Args:
        db (Session): The database session.
        id (int): The ID of the FLRoundMetric to remove.

    Returns:
        FLRoundMetric | None: The removed FLRoundMetric object if found and deleted, else None.

    """
    obj = db.get(FLRoundMetric, id)
    if obj:
        db.delete(obj)
        db.commit()
    return obj


def update(
    db: Session, db_obj: FLRoundMetric, obj_in: FLRoundMetricUpdate
) -> FLRoundMetric:
    """Updates an existing FLRoundMetric record.

    Args:
        db (Session): The database session.
        db_obj (FLRoundMetric): The existing FLRoundMetric object from the database.
        obj_in (FLRoundMetricUpdate): Pydantic model with the updated data.

    Returns:
        FLRoundMetric: The updated FLRoundMetric object.

    """
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)

    for field in update_data:
        setattr(db_obj, field, update_data[field])

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
