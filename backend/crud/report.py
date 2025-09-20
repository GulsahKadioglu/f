"""report.py

This file provides the Create, Read, Update, Delete (CRUD) operations for the
`AnalysisReport` database model. It encapsulates the logic for interacting with
the database specifically for analysis report records, including their creation,
retrieval, and aggregation of statistics.

Purpose:
- To abstract database interactions for analysis reports from the API layer.
- To provide functions for creating new analysis reports.
- To retrieve single or multiple analysis reports, with options for filtering and pagination.
- To calculate and retrieve aggregated statistics about reports.

Key Components:
- `AnalysisReport`: The SQLAlchemy ORM model representing an analysis report in the database.
- `ReportCreate`, `ReportStatistics`: Pydantic schemas for validating input data and structuring output.
- `Session`: SQLAlchemy database session for performing database operations.
"""

import uuid
from typing import TypeVar

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.models.report import AnalysisReport
from backend.schemas.report import (
    ReportCreate,
    ReportStatistics,
    ReportStatus,
    ReportUpdate,
)

from backend.models import report as models

ModelType = TypeVar("ModelType", bound=AnalysisReport)


def get_report(db: Session, report_id: int) -> models.AnalysisReport | None:
    """Retrieves a single analysis report record by its unique identifier.

    Args:
        db (Session): The SQLAlchemy database session.
        report_id (int): The unique integer ID of the analysis report to retrieve.

    Returns:
        models.AnalysisReport: The `AnalysisReport` ORM object if found; otherwise, `None`.

    """
    return (
        db.query(models.AnalysisReport)
        .filter(models.AnalysisReport.id == report_id)
        .first()
    )


def get_reports(
    db: Session, *, user_id: uuid.UUID | None = None, skip: int = 0, limit: int = 100
) -> list[models.AnalysisReport]:
    """Retrieves a paginated list of multiple analysis report records, optionally filtered by owner.

    This function queries the database for `AnalysisReport` records and applies
    pagination using `skip` (offset) and `limit` parameters. If a `user_id` is provided,
    it filters the reports to only include those owned by that user.

    Args:
        db (Session): The SQLAlchemy database session.
        user_id (uuid.UUID | None): The UUID of the user whose reports are to be retrieved.
                                    If None, all reports are returned (e.g., for admin access).
        skip (int): The number of records to skip (offset) for pagination. Defaults to 0.
        limit (int): The maximum number of records to return (limit) for pagination. Defaults to 100.

    Returns:
        list[models.AnalysisReport]: A list of `AnalysisReport` ORM objects.

    """
    query = db.query(models.AnalysisReport)
    if user_id:
        query = query.filter(models.AnalysisReport.doctor_id == user_id)
    return query.offset(skip).limit(limit).all()


def create_report(
    db: Session, report: ReportCreate, owner_id: uuid.UUID
) -> AnalysisReport:
    """Creates a new analysis report record in the database, associating it with a specific owner.

    This function takes the input data for a new analysis report, constructs an
    `AnalysisReport` ORM object, adds it to the session, commits the transaction,
    and refreshes the object to load any
    database-generated fields (like the ID or creation timestamp).

    Args:
        db (Session): The SQLAlchemy database session.
        report (ReportCreate): A Pydantic schema object containing the data
                               for the new analysis report.
        owner_id (uuid.UUID): The UUID of the user (doctor) who owns this report.

    Returns:
        AnalysisReport: The newly created `AnalysisReport` ORM object, as it exists in the database.

    """
    db_obj = AnalysisReport(
        model_version=report.model_version,
        diagnosis_result=report.diagnosis_result,
        image_count=report.image_count,
        status=report.status,
        final_confidence_score=report.final_confidence_score,
        doctor_id=owner_id,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_report_statistics(db: Session) -> ReportStatistics:
    """Calculates and retrieves aggregated statistics about analysis reports.

    This function queries the database to count reports by status (completed, pending, failed),
    calculate the average confidence score for completed reports, determine the distribution
    of diagnosis results, and compute the average number of images per report.

    Args:
        db (Session): The SQLAlchemy database session.

    Returns:
        ReportStatistics: A Pydantic model containing the aggregated statistics.

    """
    total_reports = db.query(AnalysisReport).count()
    completed_reports = (
        db.query(AnalysisReport)
        .filter(AnalysisReport.status == ReportStatus.COMPLETED)
        .count()
    )
    pending_reports = (
        db.query(AnalysisReport)
        .filter(AnalysisReport.status == ReportStatus.PENDING)
        .count()
    )
    failed_reports = (
        db.query(AnalysisReport)
        .filter(AnalysisReport.status == ReportStatus.FAILED)
        .count()
    )

    completed_reports_with_score = (
        db.query(AnalysisReport)
        .filter(
            AnalysisReport.status == ReportStatus.COMPLETED,
            AnalysisReport.final_confidence_score.isnot(None),
        )
        .all()
    )

    if completed_reports_with_score:
        total_confidence_score = sum(
            [r.final_confidence_score for r in completed_reports_with_score]
        )
        avg_confidence_score = total_confidence_score / len(
            completed_reports_with_score
        )
    else:
        avg_confidence_score = None

    diagnosis_distribution = (
        db.query(
            AnalysisReport.diagnosis_result, func.count(AnalysisReport.diagnosis_result)
        )
        .group_by(AnalysisReport.diagnosis_result)
        .all()
    )

    diagnosis_dict = {
        diag: count for diag, count in diagnosis_distribution if diag is not None
    }

    total_images = db.query(func.sum(AnalysisReport.image_count)).scalar()
    if total_reports > 0 and total_images is not None:
        avg_images_per_report = total_images / total_reports
    else:
        avg_images_per_report = None

    return ReportStatistics(
        total_reports=total_reports,
        completed_reports=completed_reports,
        pending_reports=pending_reports,
        failed_reports=failed_reports,
        avg_confidence_score=avg_confidence_score,
        diagnosis_distribution=diagnosis_dict,
        avg_images_per_report=avg_images_per_report,
    )


def update(
    db: Session, *, db_obj: models.AnalysisReport, obj_in: ReportUpdate | dict
) -> models.AnalysisReport:
    """Updates an existing AnalysisReport record.

    Args:
        db (Session): The database session.
        db_obj (models.AnalysisReport): The existing AnalysisReport object from the database.
        obj_in (ReportUpdate | dict): Pydantic model or dictionary with the updated data.

    Returns:
        models.AnalysisReport: The updated AnalysisReport object.

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


def remove(db: Session, *, id: int) -> models.AnalysisReport | None:
    """Removes an AnalysisReport record by its ID.

    Args:
        db (Session): The database session.
        id (int): The ID of the AnalysisReport to remove.

    Returns:
        models.AnalysisReport | None: The removed AnalysisReport object if found and deleted, else None.

    """
    obj = db.query(models.AnalysisReport).get(id)
    if obj:
        db.delete(obj)
        db.commit()
    return obj
