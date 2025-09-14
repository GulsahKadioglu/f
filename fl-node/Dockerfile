# Dockerfile for the Federated Learning Node (Client) application.
#
# This Dockerfile defines the steps to build a Docker image for the FL client.
# The FL client is responsible for training a local model on its private data
# and securely exchanging encrypted model updates with the central FL server.
#
# Purpose:
# - To create a reproducible and isolated environment for the FL client.
# - To package all necessary dependencies and application code into a single image.
# - To facilitate easy deployment and scaling of FL clients.
#
# Key Stages:
# 1. Base Image Selection: Uses a lightweight Python image.
# 2. Working Directory: Sets the application directory inside the container.
# 3. Dependency Installation: Installs Python packages required by the application.
# 4. Application Code Copy: Copies the FL client application code into the image.
# 5. Command Definition: Specifies the command to run when the container starts.

# Stage 1: Builder
# This stage is used to install build-time dependencies and Python packages.
# Using a multi-stage build helps to keep the final image size small.
FROM python:3.11 AS builder

# Set the working directory inside the container.
WORKDIR /app

# Copy the requirements file into the builder stage.
COPY ./requirements.txt /app/requirements.txt

# Install build dependencies and Python packages.
# `apt-get update` and `apt-get install -y build-essential` are for compiling certain Python packages.
# `rm -rf /var/lib/apt/lists/*` cleans up the apt cache.
# `pip install --no-cache-dir --upgrade -r /app/requirements.txt` installs core Python dependencies.
# The subsequent `pip install` commands are for specific libraries (torch, torchvision, torchaudio, monai)
# that might require specific installation methods or versions.
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade -r /app/requirements.txt && \
    pip install --no-cache-dir torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir monai==1.5.0

# Stage 2: Runtime
# This stage creates the final, smaller image by copying only the necessary files from the builder stage.
FROM python:3.11-slim

# Set the working directory inside the container.
WORKDIR /app

# Copy only the installed Python packages from the builder stage to the runtime stage.
# This significantly reduces the final image size by not including build tools.
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy the application code into the container.
COPY . /app

# Command to run the FL client application.
# `python -m src.client`: Executes the client script as a module.
CMD ["python", "-m", "src.client"]