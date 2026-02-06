"""
Main application entry point for the Todo application backend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from .database.init_db import create_db_and_tables
from .routes import tasks
from .routes.auth import router as auth_router
from .middleware import http_exception_handler, general_exception_handler

# Create FastAPI application instance
app = FastAPI(
    title="Todo Application API",
    description="REST API for the Todo application with user authentication and task management",
    version="1.0.0"
)

# Add exception handlers
app.add_exception_handler(422, http_exception_handler)  # RequestValidationError
app.add_exception_handler(400, http_exception_handler)  # HTTPException
app.add_exception_handler(401, http_exception_handler)  # HTTPException
app.add_exception_handler(403, http_exception_handler)  # HTTPException
app.add_exception_handler(404, http_exception_handler)  # HTTPException
app.add_exception_handler(500, general_exception_handler)  # General exceptions

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include task routes
app.include_router(tasks.router)

# Include auth routes
app.include_router(auth_router)

@app.on_event("startup")
async def startup_event():
    """
    Event handler for application startup.
    Initializes database tables.
    """
    create_db_and_tables()

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
        "documentation": "/docs"
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint for the API.

    Returns:
        API health status
    """
    return {
        "status": "healthy",
        "service": "Todo Application API"
    }