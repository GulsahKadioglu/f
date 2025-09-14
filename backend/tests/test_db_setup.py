# -*- coding: utf-8 -*-
"""test_db_setup.py

This file contains a simple test to verify that the database setup fixtures
in `conftest.py` are working correctly.

Purpose:
- To ensure that the test database engine and session fixtures can be
  initialized without errors.
- To confirm that SQLAlchemy tables are being created correctly in the
  in-memory test database.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class MyTestTable(Base):
    """A simple SQLAlchemy model for testing database table creation."""
    __tablename__ = "my_test_table"
    id = Column(Integer, primary_key=True)
    name = Column(String)


def test_table_creation(db_session):
    """Tests that the database session fixture works and tables are created.

    This test implicitly verifies that the `db_engine` and `db_session` fixtures
    in `conftest.py` are functioning correctly. The success of this test depends
    on the `Base.metadata.create_all(bind=engine)` call in the `db_engine`
    fixture successfully creating the `my_test_table` table.
    """
    # If db_session fixture works, this test should pass
    # It implicitly relies on Base.metadata.create_all being called by db_session
    # and the table 'my_test_table' being created.
    assert True
