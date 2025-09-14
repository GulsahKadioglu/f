# Development Guide

## Introduction

This document provides a more in-depth guide for developers contributing to the platform. It assumes you have already followed the setup instructions in `README.md`.

## Architecture Deep Dive

*(This section can be expanded with more detailed diagrams and explanations of how the services interact, data flow for specific features, and API contracts.)*

- **Backend:** Built with FastAPI, follows a standard repository pattern for database interactions (`/crud`), Pydantic schemas for data validation (`/schemas`), and Alembic for migrations.
- **Frontend:** A standard Next.js application using Server-Side Rendering (SSR) and static generation where appropriate. API communication is handled via an Axios client.

## Coding Style & Conventions

To maintain code quality and consistency, we use the following tools and standards:

- **Python (Backend & FL-Node):**
  - **Linter/Formatter:** We use `Ruff` for linting and `Black` for formatting. Please run these tools before committing your code.
  - **Type Hinting:** All new functions and methods should include type hints.

- **TypeScript/JavaScript (Frontend):**
  - **Linter/Formatter:** We use `ESLint` for linting and `Prettier` for formatting. These are configured to run on save and as a pre-commit hook.

## Database Migrations

Database schema changes are managed by Alembic.

- **To create a new migration:** After changing a SQLAlchemy model in `/models`, run the following command inside the `backend` container:
  ```bash
  alembic revision --autogenerate -m "A descriptive message about the changes"
  ```
- **To apply migrations:** This is handled automatically when the `backend` service starts, as defined in the `docker-compose.yml` command.

## Testing

Running tests is a critical part of our development workflow. Here is how to run the tests for each part of the application.

### Backend & FL-Node Tests

The Python-based services (`backend` and `fl-node`) use `pytest`.

To run the tests, navigate to the respective directory (`backend/` or `fl-node/`) and run the following command:

```bash
pytest
```

You can also run tests from within the running Docker containers if you prefer.

### Frontend Tests

The frontend has both unit tests (Jest) and end-to-end tests (Playwright).

- **To run the unit tests:**
  Navigate to the `frontend/` directory and run:
  ```bash
  npm test
  ```

- **To run the end-to-end tests:**
  Navigate to the `frontend/` directory and run:
  ```bash
  npm run test:e2e
  ```
