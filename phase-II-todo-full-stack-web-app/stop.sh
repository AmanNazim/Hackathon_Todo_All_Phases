#!/bin/bash

# Stop Todo Application
# This script stops the backend and frontend servers

set -e

echo "🛑 Stopping Todo Application..."
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Stop Backend
if [ -f "logs/backend.pid" ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        echo -e "${GREEN}✓ Backend stopped${NC}"
    else
        echo "Backend process not found"
    fi
    rm logs/backend.pid
else
    echo "No backend PID file found"
fi

# Stop Frontend
if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        echo -e "${GREEN}✓ Frontend stopped${NC}"
    else
        echo "Frontend process not found"
    fi
    rm logs/frontend.pid
else
    echo "No frontend PID file found"
fi

echo ""
echo -e "${GREEN}✓ Application stopped${NC}"
