"""__init__.py (CRUD Package Initialization)

This file serves as the initialization file for the `crud` (Create, Read, Update, Delete)
package. It aggregates and exposes all individual CRUD modules, making them easily
importable and accessible from other parts of the application (e.g., API endpoints).

Purpose:
- To provide a centralized entry point for all database interaction logic.
- To simplify imports for CRUD operations throughout the application.
- To maintain a clear separation of concerns between API logic and database operations.

Key Components:
- Imports individual CRUD modules (e.g., `user`, `medical_case`, `medical_image`,
  `model_version`, `report`), making their functions available under the `crud` namespace.
"""

from . import fl_metric, medical_case, medical_image, model_version, report, user

__all__ = [
    "user",
    "medical_case",
    "medical_image",
    "model_version",
    "report",
    "fl_metric",
]
