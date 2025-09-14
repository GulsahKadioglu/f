# Federated Cancer Screening Platform

A platform for privacy-preserving, federated machine learning for cancer screening. It allows multiple institutions to collaboratively train a central AI model without sharing sensitive patient data.

## Core Features

- **Secure Federated Learning:** Utilizes the Flower framework with Homomorphic Encryption (HE) to ensure patient data privacy during model training.
- **Web & Mobile Interface:** A Next.js web application for administrators and doctors, and a React Native mobile app for data collection and case management.
- **RESTful API:** A robust backend built with FastAPI, handling business logic, data persistence, and serving the frontend applications.
- **System Monitoring:** Integrated monitoring stack with Prometheus and Grafana to observe system health and performance.
- **Containerized Deployment:** The entire application is containerized with Docker for easy setup, scalability, and consistent environments.

## System Architecture

The platform is composed of several microservices orchestrated by Docker Compose:

| Service | Technology | Purpose |
|---|---|---|
| `frontend` | Next.js | The main web interface for doctors and administrators. |
| `backend` | FastAPI (Python) | The core API for business logic, authentication, and database operations. |
| `db` | PostgreSQL | The primary relational database for storing user, case, and report data. |
| `redis` | Redis | Used as a message broker for background tasks and for caching. |
| `celery-worker` | Celery (Python) | Handles asynchronous background tasks. |
| `flower-server` | Flower (Python) | The central server for orchestrating the federated learning process. |
| `fl-node` | Flower (Python) | Represents a client node (e.g., a hospital) that participates in federated training. |
| `nginx` | Nginx | A reverse proxy for routing traffic to the frontend and backend services. |
| `prometheus` | Prometheus | Collects and stores system and application metrics. |
| `grafana` | Grafana | Visualizes metrics collected by Prometheus in dashboards. |

## Getting Started

Follow these instructions to get the entire platform running locally using Docker.

### Prerequisites

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/federated-cancer-screening.git
cd federated-cancer-screening
```

### 2. Configure Environment Variables

The backend service requires environment variables to run.

- Navigate to the `backend` directory.
- Create a `.env` file by copying the example file:
  ```bash
  cp .env.example .env
  ```
- Open the new `.env` file and set the required variables, especially `SECRET_KEY`.

### 3. Build and Run the Application

From the project's root directory, run the following command:

```bash
docker-compose up --build
```

This single command will:
- Build the Docker images for all services.
- Start all the containers in the correct order.
- Automatically apply database migrations for the backend.

## Accessing Services

Once the containers are running, you can access the various parts of the application:

| Service | URL |
|---|---|
| **Frontend UI** | [http://localhost:3000](http://localhost:3000) |
| **Backend API Docs** | [http://localhost:8000/docs](http://localhost:8000/docs) |
| **Flower FL Server** | [http://localhost:8080](http://localhost:8080) |
| **Grafana Dashboard** | [http://localhost:3001](http://localhost:3001) |
| **Prometheus** | [http://localhost:9090](http://localhost:9090) |

## API Examples

Here are a few examples of how to interact with the backend API using `curl`. The base URL for the API is `http://localhost:8000/api/v1`.

### 1. Create a New User

This endpoint allows for the public registration of a new user.

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/users/' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "doctor@example.com",
  "password": "a_strong_password",
  "role": "doctor"
}'
```

### 2. Login and Get Access Token

After creating a user, you can log in to receive a JWT access token, which is required for authenticated requests.

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/login/access-token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=doctor@example.com&password=a_strong_password'
```

The response will be a JSON object containing your `access_token`.

### 3. Access a Protected Endpoint

Use the `access_token` from the login step as a Bearer token in the `Authorization` header to access protected endpoints.

For example, to get a list of all medical cases (assuming you have the correct permissions):

```bash
# First, store your token in a shell variable
export ACCESS_TOKEN="YOUR_ACCESS_TOKEN_FROM_LOGIN"

# Then, make the authenticated request
curl -X 'GET' \
  'http://localhost:8000/api/v1/medical-cases/' \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

## Contributing

Contributions are welcome. Please refer to `CONTRIBUTING.md` for more details on the development process and how to submit pull requests.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more information.
