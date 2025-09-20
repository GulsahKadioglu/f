"""env.py

This is the main configuration file for Alembic, the database migration tool
used by the application. It is executed when the `alembic` command is run.

Purpose:
- To configure the connection to the database for migration operations.
- To define how migrations are run, either "online" (connected to a database)
  or "offline" (generating SQL scripts).
- To specify the target metadata, which is the SQLAlchemy model definition
  that Alembic compares against the database to detect changes.

Key Sections:
- **Alembic Configuration**: Loads the configuration from the `alembic.ini` file.
- **Target Metadata**: Specifies the `Base.metadata` from the application's
  models, which Alembic uses to understand the desired database schema.
- **Migration Functions**: `run_migrations_offline` and `run_migrations_online`
  define the two modes of operation for applying migrations.
- **Execution Block**: Determines whether to run in offline or online mode based
  on the command-line arguments passed to Alembic.
"""

import os
from logging.config import fileConfig

# Import the Base metadata object from the application's database models.
# This is crucial as it tells Alembic what the target schema should look like.
from backend.db.base_class import Base
from sqlalchemy import engine_from_config, pool

from alembic import context

# --- Alembic Configuration ---
# This is the Alembic Config object, which provides access to the values
# within the .ini file in use (e.g., `alembic.ini`).
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers based on the .ini file's logging configuration.
if config.config_file_name:
    fileConfig(config.config_file_name)

# Set the target metadata for Alembic. Alembic uses this metadata object
# to compare with the current state of the database and generate migrations.
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This mode is used to generate SQL scripts for the migrations without
    requiring a live database connection. The context is configured with a URL,
    and the migration output is typically written to standard output or a file.
    This is useful for reviewing migration scripts before applying them or for
    deployments where direct database access from the build environment is not
    possible.
    """
    # Get the database URL from the config file.
    url = config.get_main_option("sqlalchemy.url")
    # If no URL is found, use a temporary SQLite database for autogeneration.
    if url is None:
        url = "sqlite:////tmp/test.db"
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,  # Render literal values in SQL scripts.
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this mode, Alembic connects to the target database using an SQLAlchemy
    Engine and applies the migrations directly. This is the most common mode
    of
    operation during development and for automated deployments. The database
    connection details are retrieved from the environment or the `alembic.ini`
    file.
    """
    # Create an SQLAlchemy engine from the configuration.
    # It prioritizes the DATABASE_URL environment variable for the connection.
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # Use NullPool to avoid connection pooling issues.
        url=os.environ.get("DATABASE_URL"),  # Pass DATABASE_URL directly
    )

    with connectable.connect() as connection:
        # Configure the migration context with the live database connection.
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


# Determine whether to run in offline or online mode.
# The `autogenerate` command implies offline mode to generate the script.
if context.is_offline_mode() or getattr(config.cmd_opts, "autogenerate", False):
    print("Running migrations in offline mode...")
    run_migrations_offline()
else:
    print("Running migrations in online mode...")
    run_migrations_online()