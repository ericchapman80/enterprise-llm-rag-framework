#!/bin/bash
# 
# Script: run-local-native.sh
# Description: Runs the RAG-LLM Framework backend natively (without containers).
#              Sets up a Python virtual environment, installs dependencies,
#              ensures Ollama is running, and starts the backend service.
# 
# Usage: ./scripts/run-local-native.sh
# 
# Requirements:
#   - Python 3.8+ installed
#   - Ollama installed (or will provide instructions)
# 
# Notes:
#   - Creates a Python virtual environment in ./rag-llm-env
#   - Installs dependencies from src/backend/requirements.txt
#   - Creates a default .env file if it doesn't exist
#   - Starts Ollama service if not already running
#   - Downloads the tinyllama model if not already downloaded
#   - Creates necessary directories and configuration files
# 

set -e

echo "=== Starting RAG-LLM Backend Natively ==="

if [ ! -d "rag-llm-env" ]; then
    echo "Creating Python virtual environment..."
    python -m venv rag-llm-env
fi

echo "Activating virtual environment..."
source rag-llm-env/bin/activate

echo "Installing backend dependencies..."
pip install -r src/backend/requirements.txt

echo "Ensuring python-multipart is installed..."
pip install python-multipart

if [ ! -f ".env" ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "Please edit .env file with your credentials"
fi

echo "Loading environment variables..."
export $(grep -v '^#' .env | xargs)

if ! command -v ollama &> /dev/null; then
    echo "Ollama is not installed. Please install it first:"
    echo "  - macOS: brew install ollama"
    echo "  - Linux: curl -fsSL https://ollama.com/install.sh | sh"
    echo "  - Windows: Download from https://ollama.com/download"
    exit 1
fi

if ! curl -s http://localhost:11434/api/version &> /dev/null; then
    echo "Starting Ollama service..."
    ollama serve &
    sleep 5
fi

if ! ollama list | grep -q "tinyllama"; then
    echo "Pulling tinyllama model (this may take a while)..."
    ollama pull tinyllama
fi

mkdir -p data/chroma_db
mkdir -p src
mkdir -p src/backend
mkdir -p config

touch src/__init__.py
touch src/backend/__init__.py

if [ ! -f "config/config.yaml" ]; then
    echo "Creating default config file..."
    cat > config/config.yaml << EOF
llm:
  provider: "ollama"
  model: "tinyllama"
  temperature: 0.7
  max_tokens: 2048

vector_db:
  provider: "chroma"
  path: "./data/chroma_db"

embeddings:
  model: "all-MiniLM-L6-v2"
EOF
    echo "Default config file created at config/config.yaml"
fi

export PYTHONPATH=$PWD

echo "Starting FastAPI server..."
cd src/backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
