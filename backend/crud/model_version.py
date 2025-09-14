"""model_version.py

This file implements the Create, Read, Update, Delete (CRUD) operations for the
`ModelVersion` database model. It defines a generic `CRUDModelVersion` class
that provides reusable methods for interacting with model version records,
ensuring consistent data handling for federated learning models.

Purpose:
- To abstract database interactions for model versions from the API layer.
- To provide a standardized set of operations for managing model metadata,
  including version numbers, performance metrics, and file paths.

Key Components:
- `ModelVersion`: The SQLAlchemy ORM model representing a federated learning
  model version in the database.
- `ModelVersionCreate`, `ModelVersionUpdate`: Pydantic schemas for validating
  input data during creation and update operations.
- `Session`: SQLAlchemy database session for performing database operations.
- `CRUDModelVersion` class: A generic class providing common CRUD methods.
"""

from typing import Any, Dict, List, Optional, Type, TypeVar, Union

from sqlalchemy.orm import Session

from ..models.model_version import ModelVersion
from ..schemas.model_version import ModelVersionCreate, ModelVersionUpdate

ModelType = TypeVar("ModelType", bound=ModelVersion)


class CRUDModelVersion:
    """Generic CRUD (Create, Read, Update, Delete) class for the ModelVersion model.

    This class provides a set of standardized methods to interact with the
    `ModelVersion` database table. It encapsulates common database operations,
    promoting code reusability and maintainability.
    """

    def __init__(self, model: Type[ModelType]):
        """Initializes the CRUD object with a specific SQLAlchemy model.

        This constructor sets the `model` attribute, allowing the CRUD methods
        to operate on the specified database model (e.g., `ModelVersion`).

        Args:
            model (Type[ModelType]): The SQLAlchemy ORM model class (e.g., `ModelVersion`)
                                     that this CRUD instance will manage.

        """
        self.model = model

    def get(self, db: Session, id: str) -> Optional[ModelType]:
        """Retrieves a single model version record by its unique identifier.

        Args:
            db (Session): The SQLAlchemy database session.
            id (str): The unique identifier (ID) of the model version to retrieve.

        Returns:
            Optional[ModelType]: The `ModelVersion` ORM object if found; otherwise, `None`.

        """
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Retrieves a paginated list of multiple model version records.

        This method queries the database for `ModelVersion` records and applies
        pagination using `skip` (offset) and `limit` parameters.

        Args:
            db (Session): The SQLAlchemy database session.
            skip (int): The number of records to skip (offset) for pagination. Defaults to 0.
            limit (int): The maximum number of records to return (limit) for pagination. Defaults to 100.

        Returns:
            List[ModelType]: A list of `ModelVersion` ORM objects.

        """
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: ModelVersionCreate) -> ModelType:
        """Creates a new model version record in the database.

        This method takes a `ModelVersionCreate` Pydantic schema object, converts
        it into a `ModelVersion` ORM object, adds it to the database session,
        commits the transaction, and refreshes the object to load any
        database-generated fields.

        Args:
            db (Session): The SQLAlchemy database session.
            obj_in (ModelVersionCreate): A Pydantic schema object containing the data
                                         for the new model version.

        Returns:
            ModelType: The newly created `ModelVersion` ORM object, as it exists in the database.

        """
        db_obj = self.model(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,  # The existing database object to be updated.
        obj_in: Union[
            ModelVersionUpdate, Dict[str, Any]
        ],  # The new data for the update.
    ) -> ModelType:
        """Updates an existing model version record in the database.

        This method takes an existing `ModelVersion` ORM object and new data
        (either a Pydantic `ModelVersionUpdate` schema or a dictionary) and
        applies the updates. It only updates fields that are provided in `obj_in`.

        Args:
            db (Session): The SQLAlchemy database session.
            db_obj (ModelType): The existing `ModelVersion` ORM object to update.
            obj_in (Union[ModelVersionUpdate, Dict[str, Any]]): The new data to apply.
                                                                 If a Pydantic model, only
                                                                 set fields are used.

        Returns:
            ModelType: The updated `ModelVersion` ORM object.

        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: str) -> Optional[ModelType]:
        """Deletes a model version record from the database by its ID.

        Args:
            db (Session): The SQLAlchemy database session.
            id (str): The unique identifier (ID) of the model version to delete.

        Returns:
            Optional[ModelType]: The deleted `ModelVersion` ORM object if found and deleted;
                                 otherwise, `None`.

        """
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj


# Create an instance of CRUDModelVersion for the ModelVersion model.
# This instance is then imported and used throughout the application (e.g., in API routers)
# to perform CRUD operations on model versions.
model_version = CRUDModelVersion(ModelVersion)
