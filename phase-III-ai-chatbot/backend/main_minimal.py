"""Minimal FastAPI test - no routers"""

from fastapi import FastAPI
from src.config.settings import settings

app = FastAPI(
    title="Minimal Test",
    debug=True
)

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "test": "minimal"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Minimal test app"}
