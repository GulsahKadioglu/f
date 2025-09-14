# Dockerfile for the Federated Learning (FL) server.
# This file defines how the FL server's Docker image is built.

# Use a slim Python 3.11 base image for a smaller image size.
FROM python:3.11-slim

# Set the working directory inside the container.
WORKDIR /app

# Copy the requirements file into the container.
# This step is done separately to leverage Docker's build cache.
COPY requirements.txt ./
# Install Python dependencies.
# `--no-cache-dir`: Disables the pip cache, reducing image size.
# `-r requirements.txt`: Installs packages listed in requirements.txt.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code into the container.
# This should be done after installing dependencies to take advantage of Docker's build cache.
COPY . .

# Command to run the FL server application.
# `python server.py`: Executes the server script.
CMD ["python", "server.py"]