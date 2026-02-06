"""
Script to run the Todo application backend.
"""

import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    port = int(os.getenv("BACKEND_PORT", "8000"))
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    reload = os.getenv("DEV_MODE", "false").lower() == "true"

    print(f"Starting Todo Application API on {host}:{port}")
    print(f"Development mode: {reload}")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )