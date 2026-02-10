"""
Main application entry point for the Todo application backend.
"""

from contextlib import asynccontextmanager
from typing import AsyncIterator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import logging

import os

# Import from local modules (absolute imports for entry point)
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from database import create_db_and_tables
from routes import tasks
from routes.auth import router as auth_router
from routes.analytics import router as analytics_router

# Import all models to ensure they're registered with SQLModel
from models import (
    # Better Auth tables (created by SQLModel)
    BetterAuthUser, BetterAuthSession, BetterAuthAccount, BetterAuthVerification,
    # Application tables
    Task, TaskTag, TaskHistory,
    PasswordResetToken, EmailVerificationToken,
    DailyAnalytics, AnalyticsCache
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get allowed origins from environment variable
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001")
allowed_origins_list = [origin.strip() for origin in ALLOWED_ORIGINS.split(",")]
logger.info(f"CORS allowed origins: {allowed_origins_list}")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Lifespan context manager for application startup and shutdown.

    Handles:
    - Database initialization on startup
    - Resource cleanup on shutdown
    """
    # Startup: Initialize database tables
    print("Starting up: Initializing database...")
    create_db_and_tables()
    print("Database initialized successfully")

    yield

    # Shutdown: Cleanup resources
    print("Shutting down: Cleaning up resources...")


# Create FastAPI application instance with lifespan
app = FastAPI(
    title="Todo Application API",
    description="REST API for the Todo application with user authentication and task management",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins_list,  # Read from environment variable
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request size limit middleware
from middleware.request_size import RequestSizeLimitMiddleware
app.add_middleware(RequestSizeLimitMiddleware)

# Add security headers middleware
from middleware.security_headers import SecurityHeadersMiddleware
app.add_middleware(SecurityHeadersMiddleware)

# Add rate limiting middleware
from middleware.rate_limit import rate_limit_middleware
app.middleware("http")(rate_limit_middleware)

# Register comprehensive error handlers
from middleware.error_handlers import register_exception_handlers
register_exception_handlers(app)

logger.info("All middleware and error handlers registered successfully")

# Include routers
app.include_router(auth_router)
app.include_router(tasks.router)
app.include_router(analytics_router)

# Import and include profile router
from routes.profile import router as profile_router
from routes.preferences import router as preferences_router
app.include_router(profile_router)
app.include_router(preferences_router)


@app.get("/")
async def root():
    """
    Root endpoint for the API.

    Returns:
        Welcome message and API information
    """
    return {
        "message": "Welcome to the Todo Application API",
        "version": "1.0.0",
        "documentation": "/api/v1/docs"
    }


@app.get("/api/v1/health")
async def health_check():
    """
    Health check endpoint for the API.

    Returns:
        API health status
    """
    return {
        "status": "healthy",
        "service": "Todo Application API",
        "version": "1.0.0"
    }