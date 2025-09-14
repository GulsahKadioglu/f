# -*- coding: utf-8 -*-
"""run_tests.py

This script is a convenience utility for running the backend tests using pytest.
It ensures that the necessary paths are added to the system path so that pytest
can discover and import the modules correctly.

Purpose:
- To provide a simple, top-level script for running all backend tests.
- To handle the necessary modifications to `sys.path` for the tests to run.

Usage:
    python run_tests.py
"""

import os
import sys

import pytest

# Add the project root to sys.path to ensure that modules can be imported
# correctly from the root of the project.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
# Add the backend directory to sys.path to ensure that modules within the
# backend can be imported correctly.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

# Run pytest for the backend tests.
# This command will discover and run all tests in the `backend/tests` directory.
pytest.main(["backend/tests"])
