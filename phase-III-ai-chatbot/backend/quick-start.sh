#!/bin/bash

# Phase III AI Chatbot - Quick Start Script
# This script helps you set up and start the backend server

set -e  # Exit on error

echo "================================================"
echo "Phase III AI Chatbot - Quick Start"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the backend directory
if [ ! -f "main.py" ]; then
    echo -e "${RED}Error: Please run this script from the backend directory${NC}"
    echo "cd phase-III-ai-chatbot/backend"
    exit 1
fi

echo "Step 1: Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3.9 or higher.${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓ Found $PYTHON_VERSION${NC}"
echo ""

echo "Step 2: Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi
echo ""

echo "Step 3: Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

echo "Step 4: Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

echo "Step 5: Checking environment configuration..."
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}No .env file found. Creating from .env.example...${NC}"
    cp .env.example .env
    echo -e "${RED}⚠ IMPORTANT: Please edit .env file with your credentials:${NC}"
    echo "  1. Set DATABASE_URL (PostgreSQL or SQLite)"
    echo "  2. Set LLM_MODEL (e.g., openai/gpt-4o-mini)"
    echo "  3. Set LLM_API_KEY (your API key)"
    echo ""
    echo -e "${YELLOW}Press Enter after you've updated .env file...${NC}"
    read
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi
echo ""

echo "Step 6: Verifying configuration..."
if grep -q "your-api-key-here" .env; then
    echo -e "${RED}⚠ Warning: .env file still contains placeholder values${NC}"
    echo "Please update LLM_API_KEY in .env file"
    echo ""
fi

# Check if LLM_API_KEY is set
if grep -q "LLM_API_KEY=" .env && ! grep -q "LLM_API_KEY=your-api-key-here" .env; then
    echo -e "${GREEN}✓ LLM API key configured${NC}"
else
    echo -e "${RED}⚠ LLM API key not configured${NC}"
fi
echo ""

echo "Step 7: Testing imports..."
python3 -c "from src.mcp.server import mcp; print('✓ MCP server imports OK')" 2>/dev/null || echo -e "${RED}✗ MCP server import failed${NC}"
python3 -c "from src.agent_sdk.agent_service import create_task_agent; print('✓ Agent SDK imports OK')" 2>/dev/null || echo -e "${RED}✗ Agent SDK import failed${NC}"
python3 -c "from src.services.task_service import TaskService; print('✓ Task service imports OK')" 2>/dev/null || echo -e "${RED}✗ Task service import failed${NC}"
echo ""

echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "To start the backend server:"
echo -e "${GREEN}uvicorn main:app --reload --host 0.0.0.0 --port 8000${NC}"
echo ""
echo "To test the server:"
echo "  Health check: curl http://localhost:8000/health"
echo "  API docs: http://localhost:8000/docs"
echo ""
echo "To start MCP server (for Claude Desktop):"
echo -e "${GREEN}python mcp_server.py${NC}"
echo ""
echo "For detailed instructions, see INTEGRATION_GUIDE.md"
echo ""
