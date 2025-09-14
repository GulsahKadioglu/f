"""add dicom metadata to medical image

Revision ID: d534e8ebeab7
Revises: 70c3ed387da4
Create Date: 2025-08-23 15:29:18.402065

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d534e8ebeab7"
down_revision: Union[str, None] = "70c3ed387da4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "medical_images", sa.Column("study_instance_uid", sa.String(), nullable=True)
    )
    op.add_column(
        "medical_images", sa.Column("series_instance_uid", sa.String(), nullable=True)
    )
    op.add_column(
        "medical_images", sa.Column("sop_instance_uid", sa.String(), nullable=True)
    )
    op.add_column("medical_images", sa.Column("modality", sa.String(), nullable=True))
    op.add_column(
        "medical_images", sa.Column("instance_number", sa.Integer(), nullable=True)
    )
    op.create_index(
        op.f("ix_medical_images_sop_instance_uid"),
        "medical_images",
        ["sop_instance_uid"],
        unique=True,
    )
    op.create_index(
        op.f("ix_medical_images_study_instance_uid"),
        "medical_images",
        ["study_instance_uid"],
        unique=False,
    )
    op.create_index(
        op.f("ix_medical_images_series_instance_uid"),
        "medical_images",
        ["series_instance_uid"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_medical_images_series_instance_uid"), table_name="medical_images"
    )
    op.drop_index(
        op.f("ix_medical_images_study_instance_uid"), table_name="medical_images"
    )
    op.drop_index(
        op.f("ix_medical_images_sop_instance_uid"), table_name="medical_images"
    )
    op.drop_column("medical_images", "instance_number")
    op.drop_column("medical_images", "modality")
    op.drop_column("medical_images", "sop_instance_uid")
    op.drop_column("medical_images", "series_instance_uid")
    op.drop_column("medical_images", "study_instance_uid")
