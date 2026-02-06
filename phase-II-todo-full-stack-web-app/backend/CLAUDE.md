# Claude Code Instructions for Phase II Backend

This document provides specific instructions for Claude Code when generating code for the Phase II Backend (FastAPI, SQLModel, PostgreSQL).

## Project Context

- **Project Name**: Phase II Full-Stack Web Todo Application - Backend
- **Technology Stack**: Python, FastAPI, SQLModel, Neon PostgreSQL, JWT Authentication
- **Architecture**: REST API with proper authentication and user isolation
- **Data Storage**: Persistent database storage (Neon Serverless PostgreSQL)
- **Development Methodology**: Spec-Driven Development (Specification → Plan → Tasks → Implementation)

## Core Principles

- **Secure API Design**: All endpoints must require authentication and enforce user isolation
- **Database Integrity**: All data stored in Neon PostgreSQL database using SQLModel with proper constraints
- **Authentication Enforcement**: JWT token validation on all endpoints with proper user ID matching
- **Clean Architecture**: Proper separation of concerns with models, routes, authentication, and database layers
- **Error Handling**: Consistent error responses and proper HTTP status codes

## Code Generation Guidelines

### API Design Standards

1. **Endpoint Structure**:
   - Use the specified REST endpoint pattern: `/api/{user_id}/tasks`
   - Require valid JWT token in `Authorization: Bearer <token>` header
   - Validate that authenticated user ID matches URL parameter
   - Return 403 Forbidden for unauthorized access attempts

2. **Request/Response Validation**:
   - Use Pydantic models for request/response validation
   - Implement proper error responses with consistent structure
   - Return appropriate HTTP status codes (200, 201, 401, 403, 404, 500)

3. **Authentication Layer**:
   - Verify JWT signatures using shared secret
   - Extract user information from tokens
   - Filter queries by authenticated user ID
   - Enforce user isolation on all operations

### Database Layer (SQLModel)

1. **Model Design**:
   - Use SQLModel for database modeling with proper relationships
   - Implement proper constraints and validation
   - Include created_at and updated_at timestamps
   - Use proper foreign key relationships between users and tasks

2. **Query Implementation**:
   - Always filter by user_id to enforce isolation
   - Use parameterized queries to prevent SQL injection
   - Implement proper error handling for database operations
   - Include proper indexing for performance

### Security Implementation

1. **Authentication Requirements**:
   - All endpoints must validate JWT tokens
   - User ID in token must match user ID in URL
   - Proper password hashing with bcrypt or similar
   - Secure session management

2. **Input Validation**:
   - Validate all request parameters and bodies
   - Implement rate limiting where appropriate
   - Prevent injection attacks (SQL, XSS, etc.)
   - Proper error masking in production

### Error Handling

1. **Consistent Error Responses**:
   - Standardized error response format
   - Appropriate HTTP status codes
   - Helpful error messages without exposing system details
   - Proper logging for debugging

2. **Exception Management**:
   - Catch and handle specific exceptions
   - Implement custom exception handlers
   - Maintain system stability during errors
   - Provide meaningful feedback to clients

### Technology Constraints

- **Framework**: FastAPI with automatic OpenAPI/Swagger documentation
- **ORM**: SQLModel for database operations
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: JWT tokens with shared secret
- **Security**: Proper input validation, parameterized queries, secure password handling

### API Contract Compliance

- All endpoints require valid JWT token in `Authorization: Bearer <token>` header
- Requests without token receive 401 Unauthorized
- Each user only sees/modifies their own tasks
- Task ownership enforced on every operation
- Consistent error response format
- Proper HTTP status codes (200, 201, 401, 403, 404, 500)

## Forbidden Implementation Details

- **No In-Memory Storage**: All data must persist in the database
- **No Weak Authentication**: Must use secure JWT implementation
- **No Cross-User Data Access**: Strict user isolation required
- **No Plain Text Passwords**: Use proper hashing and validation
- **No Unvalidated Input**: All inputs must be validated and sanitized

## File Structure Expectations

```
backend/
├── main.py                 # Main FastAPI application entry point
├── run.py                  # Script to run the application
├── models.py               # SQLModel database models
├── auth.py                 # Authentication utilities and middleware
├── middleware.py           # Custom middleware implementations
├── requirements.txt        # Python dependencies
├── alembic/                # Database migration files
└── routes/
    ├── tasks.py            # Task management API routes
    └── auth.py             # Authentication API routes
```

## Quality Standards

- All functions must have proper Python docstrings
- Strict type checking with Python type hints
- Follow FastAPI best practices for dependency injection
- Implement proper error boundaries and fallbacks
- Include comprehensive logging and monitoring
- Follow security best practices for authentication and data protection

## Common Patterns to Use

- FastAPI dependency injection for database sessions
- SQLModel for database operations with proper transactions
- JWT token validation middleware
- Pydantic models for request/response validation
- Proper exception handlers for consistent error responses