"""Phase III AI Chatbot - FastAPI Application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config.settings import settings
from src.api import chat, chatkit

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    description="AI-powered conversational task management API"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(chatkit.router, prefix="/api", tags=["chatkit"])


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "phase-iii-chatbot"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Phase III AI Chatbot API",
        "version": "1.0",
        "docs": "/docs"
    }
