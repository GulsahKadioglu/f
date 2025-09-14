import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"  # Bu değeri benzersiz bir zaman damgası ile değiştirin
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Apply the database migration to add the model_versions table."""
    op.create_table(
        "model_versions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("avg_accuracy", sa.Float(), nullable=True),
        sa.Column("avg_loss", sa.Float(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("file_path", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_model_versions_version_number"),
        "model_versions",
        ["version_number"],
        unique=True,
    )


def downgrade():
    """Reverts the database migration by dropping the 'model_versions' table."""
    op.drop_index(op.f("ix_model_versions_version_number"), table_name="model_versions")
    op.drop_table("model_versions")
