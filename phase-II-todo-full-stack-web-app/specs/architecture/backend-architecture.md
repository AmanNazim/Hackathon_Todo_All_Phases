# Backend Architecture Specification

## Overview

This document outlines the architecture for the FastAPI backend application that serves as the API for the Todo application. The backend follows modern Python patterns with FastAPI, SQLModel, and PostgreSQL, emphasizing security, scalability, and maintainability.

## Architecture Layers

### 1. Presentation Layer
- **API Routes**: FastAPI route handlers for all endpoints
- **Request/Response Models**: Pydantic models for data validation
- **Documentation**: Auto-generated OpenAPI/Swagger documentation

### 2. Business Logic Layer
- **Service Layer**: Business logic encapsulation
- **Authentication Logic**: User authentication and authorization
- **Validation Logic**: Business rule enforcement

### 3. Data Access Layer
- **SQLModel Models**: Database models and relationships
- **Repository Layer**: Data access patterns and queries
- **Database Connections**: Async database session management

### 4. Infrastructure Layer
- **Authentication**: JWT-based authentication system
- **Security**: Rate limiting, input validation, security headers
- **Logging**: Structured logging and monitoring
- **Configuration**: Environment-based configuration management

## Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Framework | FastAPI | 0.115+ |
| Language | Python | 3.9+ |
| ORM | SQLModel | 0.0.22 |
| Database | PostgreSQL | 13+ |
| ASGI Server | Uvicorn | Latest |
| Authentication | JWT | python-jose |
| Password Hashing | Bcrypt | passlib |
| Migrations | Alembic | 1.18+ |

## API Architecture

### RESTful Design Principles
- **Resource-based URLs**: `/api/users/{user_id}/tasks`
- **Standard HTTP Methods**: GET, POST, PUT, PATCH, DELETE
- **Meaningful Status Codes**: 200, 201, 204, 400, 401, 403, 404, 500
- **JSON Responses**: Consistent response format

### API Versioning Strategy
- **URI Versioning**: `/api/v1/users/{user_id}/tasks`
- **Backward Compatibility**: Maintained for minor versions
- **Deprecation Policy**: Advance notice for breaking changes

### Endpoint Design
```
/api/{user_id}/tasks          # GET, POST
/api/{user_id}/tasks/{id}     # GET, PUT, DELETE
/api/{user_id}/tasks/{id}/complete  # PATCH
/auth/register                # POST
/auth/login                   # POST
/health                       # GET
```

## Security Architecture

### Authentication Flow
```
[Client Request]
       ↓ (JWT Token in Header)
[Authentication Middleware]
       ↓ (Token Validation)
[User Identification]
       ↓ (Permission Check)
[Route Handler]
       ↓ (User Isolation Applied)
[Database Query - User Specific]
```

### JWT Token Management
- **Token Generation**: On successful login/registration
- **Token Validation**: On protected routes
- **Token Expiration**: Short-lived access tokens
- **User Isolation**: Token user ID matches URL parameter

### Input Validation
- **Pydantic Models**: Request/response validation
- **Path Parameters**: Validation at route level
- **Query Parameters**: Type and constraint validation
- **Request Bodies**: Comprehensive validation

## Data Layer Architecture

### SQLModel Entity Design
```python
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, nullable=False)
    password_hash: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    tasks: list["Task"] = Relationship(back_populates="user")

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    title: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional[User] = Relationship(back_populates="tasks")
```

### Repository Pattern
```python
class TaskRepository:
    async def get_tasks_for_user(self, user_id: int, db: AsyncSession) -> List[Task]:
        """Retrieve all tasks for a specific user."""
        stmt = select(Task).where(Task.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create_task(self, task: Task, db: AsyncSession) -> Task:
        """Create a new task."""
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task
```

### Database Connection Management
- **Async Sessions**: Using async SQLAlchemy sessions
- **Connection Pooling**: Configured for optimal performance
- **Transaction Management**: Proper transaction boundaries
- **Error Handling**: Database-specific error handling

## Authentication Architecture

### JWT Implementation
- **Token Signing**: HS256 algorithm with secret key
- **Token Claims**: User ID and email included
- **Token Validation**: Middleware-based validation
- **Token Refresh**: Planned for future implementation

### User Isolation
- **ID Matching**: Token user ID must match URL parameter
- **Data Filtering**: All queries filtered by user ID
- **Permission Checks**: Authorization at service layer
- **Error Responses**: Consistent 403 responses for unauthorized access

## Dependency Injection Pattern

### FastAPI Dependencies
```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())
) -> TokenData:
    """Dependency to get current authenticated user."""
    token = credentials.credentials
    token_data = verify_token(token)

    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    return token_data

async def get_db_session() -> AsyncSession:
    """Dependency to get database session."""
    async with AsyncSessionLocal() as session:
        yield session
```

### Service Layer Dependencies
- **Repository Injection**: Services receive repositories
- **Configuration Injection**: Environment-specific configs
- **Logger Injection**: Structured logging setup
- **Cache Injection**: Planned for performance optimization

## Performance Architecture

### Async Programming
- **Non-blocking I/O**: All database operations async
- **Concurrency**: Efficient handling of multiple requests
- **Memory Management**: Proper resource cleanup
- **Event Loop**: Uvicorn's event loop optimization

### Caching Strategy
- **Application Level**: Planned for frequently accessed data
- **Database Level**: PostgreSQL query caching
- **HTTP Level**: Response caching headers
- **CDN Ready**: Static assets caching strategy

### Database Optimization
- **Indexing Strategy**: Proper indexes for query performance
- **Query Optimization**: Efficient SQL queries
- **Connection Management**: Optimized connection pooling
- **Batch Operations**: Bulk operations where appropriate

## Error Handling Architecture

### Exception Hierarchy
```python
class BusinessLogicError(Exception):
    """Base class for business logic errors."""
    def __init__(self, detail: str, status_code: int = 400):
        self.detail = detail
        self.status_code = status_code
        super().__init__(self.detail)

class UserNotFoundError(BusinessLogicError):
    """Raised when a user is not found."""
    def __init__(self, user_id: str):
        super().__init__(
            detail=f"User with ID {user_id} not found",
            status_code=404
        )
```

### Error Response Format
```json
{
  "error": "Error Type",
  "detail": "Human-readable error message",
  "status_code": 404,
  "timestamp": "ISO 8601 formatted timestamp"
}
```

### Logging Strategy
- **Structured Logging**: JSON-formatted log entries
- **Correlation IDs**: Trace requests across services
- **Sensitive Data**: Proper sanitization of PII
- **Log Levels**: Appropriate levels for different scenarios

## Monitoring and Observability

### Health Checks
- **Liveness Probes**: Application health endpoint
- **Readiness Probes**: Dependency health checks
- **Metrics Collection**: Performance and usage metrics
- **Alerting**: Threshold-based alerting system

### API Documentation
- **Auto-generated**: FastAPI's automatic documentation
- **Interactive**: Swagger UI and ReDoc interfaces
- **Examples**: Sample requests and responses
- **Validation**: Request/response schema validation

## Security Architecture

### Input Sanitization
- **SQL Injection**: Parameterized queries prevent injection
- **XSS Prevention**: Proper output encoding
- **Rate Limiting**: Per-endpoint rate limiting
- **Validation**: Comprehensive input validation

### Authentication Security
- **Token Security**: Secure JWT implementation
- **Password Security**: Bcrypt hashing with salt
- **Session Management**: Proper session handling
- **Secure Headers**: HTTP security headers

## Deployment Architecture

### Container Strategy
- **Docker**: Containerized deployment
- **Environment Variables**: Configuration management
- **Health Checks**: Container orchestration readiness
- **Resource Limits**: Memory and CPU constraints

### Database Management
- **Migrations**: Alembic for schema management
- **Seeding**: Development data setup
- **Backup Strategy**: Regular backup procedures
- **Connection Security**: SSL/TLS for database connections

## Testing Architecture

### Unit Testing
- **Pydantic Models**: Validation testing
- **Service Layer**: Business logic testing
- **Utility Functions**: Helper function testing
- **Mocking**: External dependency mocking

### Integration Testing
- **API Endpoints**: Full request/response testing
- **Database Operations**: ORM functionality testing
- **Authentication**: Security flow testing
- **Error Cases**: Exception handling testing

### Performance Testing
- **Load Testing**: Concurrent request handling
- **Stress Testing**: System under high load
- **Endurance Testing**: Long-running performance
- **Database Performance**: Query optimization testing

## Configuration Management

### Environment Configuration
```python
class Settings(BaseSettings):
    database_url: str = Field(..., env="DATABASE_URL")
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    debug: bool = Field(False, env="DEBUG")
    environment: str = Field("production", env="ENVIRONMENT")

    class Config:
        env_file = ".env"
```

### Feature Flags
- **Environment-based**: Different features per environment
- **Gradual Rollouts**: Controlled feature releases
- **A/B Testing**: Experimental feature testing
- **Emergency Toggles**: Quick feature disabling

## Future Extensibility

### Microservice Readiness
- **Modular Design**: Easy separation of concerns
- **API Gateway**: Planned for microservice architecture
- **Message Queue**: Async task processing readiness
- **Service Discovery**: Planned for distributed systems

### Scaling Considerations
- **Horizontal Scaling**: Stateless design for scaling
- **Database Scaling**: Read replicas and sharding readiness
- **Caching Layer**: Redis integration planned
- **CDN Integration**: Static asset delivery optimization

## Quality Assurance

### Code Quality
- **Type Checking**: Strict Python typing
- **Linting**: Comprehensive code linting
- **Security Scanning**: Vulnerability detection
- **Performance Profiling**: Bottleneck identification

### API Quality
- **Contract Testing**: API contract validation
- **Documentation**: Comprehensive API documentation
- **Versioning**: Proper API version management
- **Backwards Compatibility**: Maintained for stable APIs