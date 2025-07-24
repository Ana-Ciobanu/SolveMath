# Math Operations Microservice

## Overview

This project implements a microservice for solving mathematical operations via a RESTful API. The service supports three main operations: calculating the power of a number, finding the n-th Fibonacci number, and computing the factorial of a number. The service is built using FastAPI, follows best practices for microservice architecture, and is designed for extensibility, maintainability, and security.

## Features

- **RESTful API**: Exposes endpoints for mathematical operations using POST requests with Pydantic-based request/response models.
- **User Authentication & Authorization**: Implements JWT-based authentication. Only authenticated users can access the math endpoints, and only users with the `admin` role can access the `/admin/metrics` endpoint.
- **Database Persistence**: All requests to the API are persisted in a SQLite database using SQLAlchemy ORM. This allows for auditing and analytics.
- **Caching**: Results of mathematical operations are cached in-memory for improved performance and reduced computation time.
- **Logging**: All significant events and errors are logged both to the console and to a dedicated database table.
- **Monitoring**: The service exposes Prometheus-compatible metrics at `/admin/metrics`, protected by admin authorization.
- **Frontend**: A simple HTML/JavaScript frontend is provided for user registration, login, and interacting with the API.

## Security & Production Readiness

- **Secrets Management**: All sensitive configuration (JWT secret, algorithm, token expiry) is stored in a `.env` file and loaded using `python-dotenv`. No data is hardcoded in the codebase.
- **Role-Based Access Control**: The admin role is required for accessing sensitive endpoints like metrics.
- **Input Validation**: Both frontend and backend validate user input to prevent invalid or malicious requests.
- **Extensibility**: The codebase is organized using MVC/MVCS patterns, making it easy to add new operations or extend functionality.
- **Containerization Ready**: The service can be easily containerized for deployment.

## How It Works

1. **User Registration & Login**: Users register and log in via the frontend. On successful login, a JWT token is issued.
2. **Authorization**: The frontend stores the JWT and includes it in the `Authorization` header for all API requests.
3. **Math Operations**: Authenticated users can access endpoints for power, Fibonacci, and factorial calculations. Requests are validated, processed, cached, logged, and persisted.
4. **Admin Metrics**: Admin users can view service metrics via the `/admin/metrics` endpoint.

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

- For demo purposes, the admin role is assigned to the user with username `admin`.
