#!/bin/bash
# 
# Script: start-api-server.sh
# Description: Starts the RAG-LLM Framework API server for testing and development.
#              Sets up the proper Python path and starts the FastAPI server.
# 
# Usage: ./scripts/start-api-server.sh
# 
# Notes:
#   - Runs on http://localhost:8000
#   - Enables hot-reload for development
#   - Sets PYTHONPATH for proper imports
# 

set -e

echo "=== Starting RAG-LLM Framework API Server ==="

cd "$(dirname "$0")/../src/backend"

export PYTHONPATH="$PYTHONPATH:$(dirname "$0")/.."

echo "Starting API server on http://localhost:8000"
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
