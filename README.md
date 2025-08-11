# Math Operations Microservice

![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-green)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.30-blue)
![JWT](https://img.shields.io/badge/JWT-python--jose-yellow)
![Redis](https://img.shields.io/badge/Redis-Streaming-red)
## Overview

This project implements a microservice for solving mathematical operations via a RESTful API. The service supports three main operations: calculating the power of a number, finding the n-th Fibonacci number, and computing the factorial of a number. The service is built using FastAPI, follows best practices for microservice architecture, and is designed for extensibility, maintainability, and security.

## Features

- **RESTful API**: Exposes endpoints for mathematical operations using POST requests with Pydantic-based request/response models.
- **User Authentication & Authorization**: Implements JWT-based authentication via HTTP-only cookies. Only authenticated users can access the math endpoints, and only users with the `admin` role can access the `/admin/metrics`, `/admin/requests`, `/admin/logs` endpoints.
- **Database Persistence**: All requests to the API are persisted in a SQLite database using SQLAlchemy ORM **and** are also published to a Redis Stream for real-time processing, analytics, or integration with other services.
- **Caching**: Results of mathematical operations are cached in-memory for improved performance and reduced computation time.
- **Logging**: All significant events and errors are logged to a dedicated database table.
- **Monitoring**: The service exposes Prometheus-compatible metrics at `/admin/metrics`, protected by admin authorization.
- **Frontend**: A simple HTML/JavaScript frontend is provided for user registration, login, and interacting with the API.

## How It Works

1. **User Registration & Login**: Users register and log in via the frontend. On successful login, the backend issues a JWT token as an **HTTP-only cookie**.
2. **Authorization**: The frontend does **not** store or access the JWT token directly. Instead, all API requests are made with `credentials: "include"` so the browser automatically sends the authentication cookie.
3. **Math Operations**: Authenticated users can access endpoints for power, Fibonacci, and factorial calculations. Requests are validated, processed, cached, logged, and persisted.
4. **Admin Metrics**: Admin users can view service metrics via the `/admin/metrics` endpoint, requests to the math operations API via `/admin/requests`, and logs via `/admin/logs`. The frontend determines admin access by calling the `/me` endpoint, which returns the user's role.

## Security & Production Readiness

- **HTTP-only Cookie Authentication**: Authentication tokens are stored as HTTP-only cookies, which are not accessible to JavaScript, providing protection against XSS attacks.
- **Frontend Authorization**: The frontend checks authentication and user role by calling the `/me` endpoint after login and on page load, and shows/hides admin features accordingly.
- **No Token in JS**: The frontend never stores or decodes JWT tokens in JavaScript; all authentication is handled via secure cookies.

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
    - The user's role is checked for access to protected endpoints.
