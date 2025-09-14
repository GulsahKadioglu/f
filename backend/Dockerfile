# Dockerfile for the backend application.
# This file defines how the backend application's Docker image is built.

# Use a slim Python 3.11 base image for a smaller image size.
# This provides a minimal Python environment, reducing the final image footprint.
FROM python:3.11-slim

# Install system-level dependencies required by the application.
# `apt-get update` updates the package list.
# `apt-get install -y --no-install-recommends` installs packages without prompting
# and avoids installing recommended but not strictly necessary packages.
# `postgresql-client` is needed to interact with the PostgreSQL database.
# `rm -rf /var/lib/apt/lists/*` cleans up the apt cache to reduce image size.
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
 && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container.
# All subsequent commands will be executed relative to this directory.
WORKDIR /app

# Copy the Python dependency requirements file into the container.
# This step is done separately to leverage Docker's build cache.
COPY ./requirements.txt /app/requirements.txt

# Install Python dependencies.
# `--no-cache-dir`: Disables the pip cache, reducing the final image size.
# `--upgrade`: Ensures all packages are upgraded to their latest versions.
# `-r /app/requirements.txt`: Installs packages listed in requirements.txt.
# The subsequent `pip install` commands are for specific libraries (torch, torchvision, torchaudio, captum)
# that might have complex dependencies or require specific installation methods.
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt && \
    pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir captum

# Copy the entire application code into the container.
# This should be done after installing dependencies to take advantage of Docker's build cache.
COPY . .

# Command to run the application in production using Gunicorn with Uvicorn workers.
# Gunicorn: A WSGI HTTP server for Unix, used to manage Uvicorn worker processes.
# `main:app`: Specifies the FastAPI application entry point (the `app` object in the `main.py` module).
# `--workers 4`: Configures 4 Uvicorn worker processes for concurrency.
# `--worker-class uvicorn.workers.UvicornWorker`: Specifies Uvicorn's ASGI worker class.
# `--bind 0.0.0.0:8000`: Binds the server to all network interfaces on port 8000, making it accessible from outside the container.
CMD ["gunicorn", "main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
