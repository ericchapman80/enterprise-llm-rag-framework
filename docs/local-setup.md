# Local Setup Guide for RAG-LLM Framework

This guide explains how to run the RAG-LLM framework directly on your local machine without Kubernetes, making it easier to test and develop.

## Prerequisites

- Docker and Docker Compose
- Python 3.10 or higher
- pip (Python package manager)

## Step 1: Install Ollama

Ollama is a lightweight LLM server that runs locally on your machine.

### For macOS:

```bash
brew install ollama
```

### For Linux:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### For Windows:

Download the installer from [Ollama's website](https://ollama.com/download).

## Step 2: Pull the LLM Model

```bash
# Start Ollama service
ollama serve

# In another terminal, pull the model
ollama pull llama2
```

## Step 3: Set Up Environment Variables

```bash
# Copy the example .env file
cp .env.example .env

# Edit the .env file with your credentials
# For local development, you can use these defaults:
# OLLAMA_BASE_URL=http://localhost:11434
```

## Step 4: Run with Docker Compose

The simplest way to run the entire stack is using Docker Compose:

```bash
# Build and start all services
docker-compose up --build
```

This will start:
- The RAG backend service on port 8000
- The Slack bot service (if configured)

## Step 5: Run Backend Directly (Alternative)

If you prefer to run the backend directly without Docker:

```bash
# Install dependencies
cd src/backend
pip install -r requirements.txt

# Set environment variables
export PYTHONPATH=$PWD/../..
export CONFIG_PATH=../../config/config.yaml
export OLLAMA_BASE_URL=http://localhost:11434

# Run the FastAPI server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Step 6: Test the Backend

Open your browser and navigate to:
- http://localhost:8000/health - Should return a health status
- http://localhost:8000/docs - Swagger UI for API documentation

## Step 7: Run the Slack Bot (Optional)

If you want to run the Slack bot:

```bash
# Install dependencies
cd src/integrations/slack
pip install -r requirements.txt

# Set environment variables from your .env file
export SLACK_BOT_TOKEN=your-bot-token
export SLACK_APP_TOKEN=your-app-token
export SLACK_SIGNING_SECRET=your-signing-secret
export BACKEND_URL=http://localhost:8000

# Run the bot
python slack_bot.py
```

## Troubleshooting

### Import Errors

If you encounter import errors when running the backend directly:

1. Make sure PYTHONPATH is set correctly:
   ```bash
   export PYTHONPATH=/path/to/rag-llm-framework
   ```

2. Check that __init__.py files exist in:
   - src/
   - src/backend/

### Ollama Connection Issues

If the backend can't connect to Ollama:

1. Ensure Ollama is running:
   ```bash
   ollama serve
   ```

2. Verify the model is downloaded:
   ```bash
   ollama list
   ```

3. Check the OLLAMA_BASE_URL in your environment:
   ```bash
   echo $OLLAMA_BASE_URL
   ```
   It should be set to `http://localhost:11434` for local development.

## Data Persistence

By default, Docker Compose will create volumes for:
- Ollama models
- Vector database storage

These volumes persist data between restarts.
