# -*- coding: utf-8 -*-
"""main.py

This file serves as the main entry point for the FastAPI backend application.
It initializes the FastAPI instance, includes various API routers for different
modules (authentication, reports, medical cases, model versions), and defines
global endpoints such as fetching the federated learning encryption context
and administrative user creation.

Purpose:
- To set up the core FastAPI application.
- To integrate modular API endpoints from `app.api`.
- To define global API endpoints with appropriate dependencies and security.
- To manage database sessions and user authentication for API access.

Key Components:
- FastAPI application instance.
- API routers for structured endpoint organization.
- Dependency injection for database sessions and user authentication.
- Endpoint for secure federated learning context distribution.
- Administrative endpoint for user management.
"""

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi_limiter import FastAPILimiter
from redis.asyncio import Redis
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

import backend.crud as crud
import backend.schemas as schemas
from backend.api import auth, fl, medical_cases, mlflow, model_versions, reports
from backend.api.routers import dashboard
from backend.core.config import settings
from backend.core.exceptions import (
    BadRequestException,
    DuplicateEntryException,
    ResourceNotFoundException,
)
from backend.core.security import (
    get_current_admin_user,
    get_current_user,
    has_permission,
)
from backend.db.session import get_db
from backend.models.user import Permission


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if not settings.TESTING:
        redis = Redis(host='redis', port=6379, encoding="utf8", decode_responses=True)
        await FastAPILimiter.init(redis)
    yield
    # Shutdown
    if not settings.TESTING:
        await FastAPILimiter.close()


from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="Federated Cancer Screening - Central Server",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Mount static files directory
app.mount(
    "/static/medical_images",
    StaticFiles(directory=settings.MEDICAL_IMAGES_STORAGE_PATH),
    name="medical_images",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # Use configurable origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Add HTTPS Redirect middleware (only if enabled in settings)
if settings.HTTPS_REDIRECT_ENABLE:
    app.add_middleware(HTTPSRedirectMiddleware)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; img-src 'self' https://fastapi.tiangolo.com data:;"
    )
    return response


app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])
app.include_router(
    medical_cases.router, prefix="/api/v1/medical-cases", tags=["medical_cases"]
)
app.include_router(
    model_versions.router, prefix="/api/v1/model-versions", tags=["model-versions"]
)
app.include_router(fl.router, prefix="/api/v1/fl", tags=["Federated Learning"])
app.include_router(mlflow.router, prefix="/api/v1/mlflow", tags=["mlflow"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])


@app.get("/")
async def root():
    """Root endpoint of the API.
    Returns a simple welcome message.
    """
    return {"message": "Welcome to the Federated Cancer Screening Backend API!"}


@app.post("/api/v1/users/create-admin", response_model=schemas.User, tags=["users"])
async def create_admin_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_admin_user: schemas.User = Depends(get_current_admin_user),
):
    """Creates a new admin user.

    This endpoint allows an existing administrator to create new user accounts
    with administrative privileges. It's a sensitive operation and requires
    proper authentication and authorization checks.

    Requires authentication as an admin user.
    """
    user = crud.user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this username already exists in the system.",
        )
    user = crud.user.create_user(db, user=user_in)
    return user


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}


# Example of a protected endpoint (requires authentication)
@app.get("/api/v1/protected-data", tags=["example"])
async def protected_data(current_user: schemas.User = Depends(get_current_user)):
    return {
        "message": f"Hello {current_user.email}, you have access to protected data!"
    }


# Example of an admin-only endpoint (requires admin authentication)
@app.get("/api/v1/admin-data", tags=["example"])
async def admin_data(
    current_admin_user: schemas.User = Depends(get_current_admin_user),
):
    return {
        "message": f"Hello admin {current_admin_user.email}, you have access to admin data!"
    }


# Example of an endpoint requiring a specific permission
@app.get("/api/v1/special-data", tags=["example"])
async def special_data(
    current_user: schemas.User = Depends(has_permission(Permission.REPORT_VIEW_OWN)),
):
    return {"message": f"Hello {current_user.email}, you have access to special data!"}


# Example of an endpoint requiring multiple permissions
@app.post("/api/v1/create-resource", tags=["example"])
async def create_resource(
    current_user: schemas.User = Depends(has_permission(Permission.CASE_MANAGE)),
    _: schemas.User = Depends(has_permission(Permission.CREATE_REPORT)),
):
    return {
        "message": f"Hello {current_user.email}, you have successfully created a resource!"
    }


# Example of an endpoint with a custom exception handler
@app.get("/api/v1/resource/{resource_id}", tags=["example"])
async def get_resource(resource_id: int):
    if resource_id == 404:
        raise ResourceNotFoundException(
            detail=f"Resource with ID {resource_id} not found."
        )
    return {"message": f"Resource {resource_id} details."}


@app.get("/api/v1/duplicate-check/{item_name}", tags=["example"])
async def check_duplicate(item_name: str):
    if item_name == "duplicate":
        raise DuplicateEntryException(detail=f"Item '{item_name}' already exists.")
    return {"message": f"Item '{item_name}' is unique."}


@app.post("/api/v1/process-request", tags=["example"])
async def process_request(data: dict):
    if not data.get("valid"):
        raise BadRequestException(detail="Invalid request data provided.")
    return {"message": "Request processed successfully."}