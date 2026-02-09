---
title: Todo App Backend
emoji: 📝
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# Todo Application Backend

FastAPI-based REST API backend for the Todo Full-Stack Web Application with comprehensive authentication, security, and task management features.

## Table of Contents

- [Overview](#overview)
- [Technology Stack](#technology-stack)
- [Features](#features)
- [Project Structure](#project-structure)
- [Setup and Installation](#setup-and-installation)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Security Features](#security-features)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)

## Overview

This backend provides a secure, scalable REST API for managing user authentication and task operations. Built with FastAPI and SQLModel, it offers automatic API documentation, type safety, and high performance.

## Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLModel**: SQL database ORM with Pydantic integration
- **PostgreSQL**: Robust relational database (NeonDB)
- **Pydantic**: Data validation and settings management
- **Python-JOSE**: JWT token handling
- **PassLib**: Password hashing with bcrypt
- **Uvicorn**: ASGI server for production
- **Alembic**: Database migration tool

## Features

### Authentication & Authorization
- JWT-based authentication
- User registration and login
- Password reset and email verification
- Secure password hashing with bcrypt
- Token-based session management
- Rate limiting on authentication endpoints

### Task Management
- Full CRUD operations for tasks
- User isolation (users only see their own tasks)
- Task priorities (low, medium, high, urgent)
- Task status tracking (todo, in_progress, review, done, blocked)
- Due dates and completion tracking
- Task tagging and categorization
- Bulk operations support

### Security
- Input validation and sanitization
- SQL injection prevention (parameterized queries)
- XSS protection
- Rate limiting
- Request size limits
- CORS configuration
- Security headers middleware
- Comprehensive error handling

### Additional Features
- User profile management
- User preferences and settings
- Analytics and reporting
- Database health checks
- Audit trails and change tracking
- Structured logging

## Project Structure

```
backend/
├── auth/                    # Authentication utilities
│   └── tokens.py           # JWT token generation and validation
├── database/               # Database utilities
│   ├── audit.py           # Audit trail system
│   ├── backup.py          # Backup and recovery
│   ├── branching.py       # NeonDB branching guide
│   ├── health_check.py    # Health monitoring
│   ├── initialize.py      # Database initialization
│   ├── security.py        # Security hardening
│   ├── utils.py           # Common operations
│   └── views.py           # Database views
├── exceptions/            # Custom exceptions
│   ├── __init__.py       # Comprehensive exception classes
│   └── auth.py           # Authentication exceptions
├── middleware/            # Custom middleware
│   ├── auth.py           # Authentication middleware
│   ├── error_handlers.py # Error handling
│   ├── rate_limit.py     # Rate limiting
│   ├── request_size.py   # Request size limits
│   └── security_headers.py # Security headers
├── models.py             # SQLModel database models
├── routes/               # API route handlers
│   ├── auth.py          # Authentication endpoints
│   ├── tasks.py         # Task management endpoints
│   ├── profile.py       # User profile endpoints
│   ├── preferences.py   # User preferences endpoints
│   ├── analytics.py     # Analytics endpoints
│   └── tags.py          # Tag management endpoints
├── schemas/             # Pydantic schemas
├── services/            # Business logic services
├── validators/          # Input validation
│   ├── auth.py         # Authentication validators
│   └── sanitization.py # Input sanitization
├── main.py             # FastAPI application entry point
├── database.py         # Database configuration
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Setup and Installation

### Prerequisites

- Python 3.10 or higher
- PostgreSQL database (or NeonDB account)
- pip or poetry for package management

### Installation Steps

1. **Clone the repository**
   ```bash
   cd phase-II-todo-full-stack-web-app/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   python -m database.initialize init
   ```

6. **Run the application**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Database
DATABASE_URL=postgresql://user:password@host/database?sslmode=require

# JWT Authentication
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Email (for password reset)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@yourdomain.com

# Application
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=info
```

### Database Configuration

The application uses NeonDB PostgreSQL. Configure your connection in `.env`:

```env
DATABASE_URL=postgresql://user:pass@host.neon.tech/db?sslmode=require
```

## API Documentation

### Interactive Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

### Authentication Endpoints

```
POST /api/v1/auth/register       - Register new user
POST /api/v1/auth/login          - Login user
POST /api/v1/auth/logout         - Logout user
POST /api/v1/auth/forgot-password - Request password reset
POST /api/v1/auth/reset-password  - Reset password with token
POST /api/v1/auth/change-password - Change password (authenticated)
POST /api/v1/auth/verify-email    - Verify email address
POST /api/v1/auth/resend-verification - Resend verification email
```

### Task Endpoints

```
GET    /api/v1/users/{user_id}/tasks           - Get all tasks
POST   /api/v1/users/{user_id}/tasks           - Create task
GET    /api/v1/users/{user_id}/tasks/{task_id} - Get task by ID
PUT    /api/v1/users/{user_id}/tasks/{task_id} - Update task
DELETE /api/v1/users/{user_id}/tasks/{task_id} - Delete task
PATCH  /api/v1/users/{user_id}/tasks/{task_id}/complete - Toggle completion
```

### Profile Endpoints

```
GET   /api/v1/profile        - Get user profile
PUT   /api/v1/profile        - Update user profile
GET   /api/v1/preferences    - Get user preferences
PUT   /api/v1/preferences    - Update user preferences
```

### Health Check

```
GET /api/v1/health - API health status
```

## Security Features

### Authentication Security

- **JWT Tokens**: Stateless authentication with configurable expiration
- **Password Hashing**: Bcrypt with salt for secure password storage
- **Rate Limiting**: Prevents brute force attacks (5 attempts per 15 minutes)
- **Token Validation**: Comprehensive token verification on protected routes

### Input Validation

- **Pydantic Models**: Automatic request/response validation
- **Input Sanitization**: XSS and SQL injection prevention
- **Email Validation**: RFC-compliant email format checking
- **Password Strength**: Enforced complexity requirements

### Request Security

- **Request Size Limits**: Prevents DoS via large payloads
- **CORS Configuration**: Controlled cross-origin access
- **Security Headers**: HSTS, X-Content-Type-Options, X-Frame-Options
- **SQL Injection Protection**: Parameterized queries via SQLModel

### Data Security

- **User Isolation**: Users can only access their own data
- **Audit Trails**: Comprehensive change tracking
- **Row-Level Security**: Database-level access control (optional)
- **Secure Token Storage**: Tokens never stored in database

## Development

### Running in Development Mode

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Database Operations

```bash
# Initialize database
python -m database.initialize init

# Verify database setup
python -m database.initialize verify

# Reset database (WARNING: deletes all data)
python -m database.initialize reset

# Run health check
python -m database.health_check
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_auth.py
```

### Test Structure

```
tests/
├── test_auth.py          # Authentication tests
├── test_tasks.py         # Task management tests
├── test_profile.py       # Profile tests
├── test_security.py      # Security tests
└── conftest.py          # Test fixtures
```

## Deployment

### Production Configuration

1. **Set environment to production**
   ```env
   ENVIRONMENT=production
   DEBUG=false
   ```

2. **Use production database**
   ```env
   DATABASE_URL=postgresql://prod-user:pass@prod-host/db?sslmode=require
   ```

3. **Configure secure secret key**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

### Running with Uvicorn

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker Deployment

```bash
# Build image
docker build -t todo-backend .

# Run container
docker run -p 8000:8000 --env-file .env todo-backend
```

## Troubleshooting

### Database Connection Issues

```bash
# Test database connection
python test_connection.py

# Check database health
python -m database.health_check
```

### Authentication Issues

- Verify SECRET_KEY is set in .env
- Check token expiration settings
- Ensure CORS origins include your frontend URL

### Performance Issues

- Enable connection pooling (already configured)
- Check database indexes
- Monitor slow queries
- Use database views for complex queries

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [NeonDB Documentation](https://neon.tech/docs)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation at `/api/v1/docs`
3. Check application logs
4. Verify environment configuration
