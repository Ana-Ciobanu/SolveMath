# Math Operations Microservice

![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-green)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.30-blue)
![JWT](https://img.shields.io/badge/JWT-python--jose-yellow)
## Overview

This project implements a microservice for solving mathematical operations via a RESTful API. The service supports three main operations: calculating the power of a number, finding the n-th Fibonacci number, and computing the factorial of a number. The service is built using FastAPI, follows best practices for microservice architecture, and is designed for extensibility, maintainability, and security.

## Features

- **RESTful API**: Exposes endpoints for mathematical operations using POST requests with Pydantic-based request/response models.
- **User Authentication & Authorization**: Implements JWT-based authentication. Only authenticated users can access the math endpoints, and only users with the `admin` role can access the `/admin/metrics`, `/admin/requests`, `/admin/logs` endpoints.
- **Database Persistence**: All requests to the API are persisted in a SQLite database using SQLAlchemy ORM. This allows for auditing and analytics.
- **Caching**: Results of mathematical operations are cached in-memory for improved performance and reduced computation time.
- **Logging**: All significant events and errors are logged to a dedicated database table.
- **Monitoring**: The service exposes Prometheus-compatible metrics at `/admin/metrics`, protected by admin authorization.
- **Frontend**: A simple HTML/JavaScript frontend is provided for user registration, login, and interacting with the API.

## Security & Production Readiness

- **Secrets Management**: All sensitive configuration (JWT secret, algorithm, token expiry) is stored in a `.env` file and loaded using `python-dotenv`. No data is hardcoded in the codebase.
- **Role-Based Access Control (RBAC)**: User roles are stored in the database. All users registered via the frontend or API are assigned the `user` role by default. The `admin` role is reserved and cannot be registered via the public API. Admin accounts are created securely using environment variables and a dedicated script. Only users with the `admin` role can access sensitive endpoints like metrics, logs, and requests.
- **Input Validation**: Both frontend and backend validate user input to prevent invalid or malicious requests.
- **Extensibility**: The codebase is organized using MVC/MVCS patterns, making it easy to add new operations or extend functionality.

## How It Works

1. **User Registration & Login**: Users register and log in via the frontend. On successful login, a JWT token is issued.
2. **Authorization**: The frontend stores the JWT and includes it in the `Authorization` header for all API requests.
3. **Math Operations**: Authenticated users can access endpoints for power, Fibonacci, and factorial calculations. Requests are validated, processed, cached, logged, and persisted.
4. **Admin Metrics**: Admin users can view service metrics via the `/admin/metrics` endpoint, requests to the math operations API via the `/admin/requests`, logs via the `/admin/logs`.

## Technologies Used

- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- JWT (python-jose)
- Passlib (bcrypt)
- Prometheus FastAPI Instrumentator
- fastapi-cache2
- python-dotenv

## Running the Service

1. Install dependencies:  
   `pip install -r requirements.txt`
2. Set up your `.env` file with the required environment variables.
3. Start the service:  
   `uvicorn app:app --reload`
4. Access the frontend at `http://localhost:8000`

## Notes

**RBAC Summary:**
    - All users are assigned the `user` role by default.
    - The `admin` role is only assigned via the admin creation script and cannot be set through registration.
    - JWT tokens include the user's role, which is checked for access to protected endpoints.
