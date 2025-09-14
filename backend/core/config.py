# -*- coding: utf-8 -*-
"""config.py

This file defines the application's configuration settings using Pydantic's
BaseSettings. It allows for loading configuration from environment variables
or a `.env` file, providing a centralized and type-safe way to manage
application settings.

Purpose:
- To centralize all application configuration in one place.
- To provide default values for settings, which can be overridden by
  environment variables.
- To ensure that configuration values have the correct data types.

Key Components:
- `Settings`: A Pydantic `BaseSettings` class that defines all the
  configuration variables for the application.
- `settings`: An instance of the `Settings` class that is imported and used
  throughout the application to access configuration values.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Defines the application's configuration settings.

    This class uses Pydantic's `BaseSettings` to automatically load settings
    from environment variables or a `.env` file. Each attribute of this class
    represents a configuration setting with a type annotation and a default value.
    """

    # Pydantic settings configuration. `env_file` specifies the file to load
    # environment variables from, and `extra="ignore"` prevents errors if
    # unknown environment variables are present.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # A secret key used for signing JWTs and other security-related functions.
    # It is crucial that this is kept secret in a production environment.
    SECRET_KEY: str = "your-secret-key"

    # The expiration time for JWT access tokens, in minutes.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # The algorithm used to sign JWTs.
    ALGORITHM: str = "HS256"

    # The connection string for the main application database.
    DATABASE_URL: str = "postgresql://user:password@host:port/dbname"

    # A flag to indicate if the application is running in testing mode.
    TESTING: bool = False

    # The local filesystem path where encrypted medical images are stored.
    MEDICAL_IMAGES_STORAGE_PATH: str = "./secure_storage/medical_images"

    # A list of allowed origins for Cross-Origin Resource Sharing (CORS).
    # A value of ["*"] allows all origins, which is convenient for development
    # but should be restricted in production.
    CORS_ORIGINS: list[str] = ["*"]

    # A flag to enable or disable HTTPS redirection middleware.
    HTTPS_REDIRECT_ENABLE: bool = False

    # The URL for the Redis server, used for Celery message brokering and caching.
    REDIS_URL: str = "redis://localhost:6379/0"


# Create an instance of the Settings class. This instance is imported and used
# by other parts of the application to access configuration values.
settings = Settings()