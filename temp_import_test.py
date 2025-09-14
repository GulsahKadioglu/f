# -*- coding: utf-8 -*-
"""temp_import_test.py

This is a temporary script used for testing imports. It adds the project
directory to the system path and attempts to import a module from the backend.

Purpose:
- To quickly test if the Python path is configured correctly for imports.
- To debug import errors during development.

"""

import sys

# Add the project directory to the system path.
# This is often necessary when running scripts from a subdirectory to ensure
# that modules from the root of the project can be found.
sys.path.append("C:/Users/gulsa/YZTA074/federated-cancer-screening/")

# Attempt to import a module from the backend.
# This will raise an ImportError if the path is not set up correctly.
import backend.db.base

# Print a success message if the import is successful.
print("Import successful!")
