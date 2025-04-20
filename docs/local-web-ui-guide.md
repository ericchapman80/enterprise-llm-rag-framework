# Running the RAG-LLM Framework Web UI Locally

This guide provides instructions for running the RAG-LLM Framework locally without Docker, including both the backend API server and the web UI.

## Prerequisites

- Python 3.8 or higher
- Git (to clone the repository)
- Ollama (optional, only needed for non-test mode)

## Quick Start

The easiest way to run the entire system locally is to use our test mode script, which starts both the backend API and web UI:

```bash
# Make the script executable
chmod +x scripts/run-test-mode.sh

# Run the system in test mode (no Ollama required)
./scripts/run-test-mode.sh
```

This will:
1. Start the backend API server on port 8000
2. Start the web UI server on port 8080
3. Configure the system to run in test mode (no real LLM required)

You can then access:
- Web UI: http://localhost:8080
- API Documentation: http://localhost:8000/docs

## Manual Setup

If you prefer to start the components separately, follow these steps:

### 1. Start the Backend API Server

```bash
# Create and activate a Python virtual environment
python -m venv rag-llm-env
source rag-llm-env/bin/activate

# Install dependencies
pip install -r src/backend/requirements.txt

# Start the backend in test mode (no Ollama required)
export PYTHONPATH=$PWD
export RAG_TEST_MODE=true
cd src/backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Start the Web UI Server

In a new terminal:

```bash
# Navigate to the web UI directory
cd src/web

# Start a simple HTTP server
python -m http.server 8080
```

You can then access the web UI at http://localhost:8080

## Troubleshooting

### Port Already in Use

If you see an error like "Address already in use", it means another process is using the port:

```bash
# Find the process using port 8000 or 8080
lsof -i :8000
lsof -i :8080

# Kill the process
kill <PID>
```

### Backend Not Starting

If the backend fails to start, check:

1. Python environment is activated
2. All dependencies are installed
3. PYTHONPATH is set correctly
4. You're in the correct directory

### Web UI Not Showing Content

If http://localhost:8080 is not serving content:

1. Verify the web server is running: `ps aux | grep "python -m http.server 8080"`
2. Check that the web files exist: `ls -la src/web/`
3. Make sure you're running the server from the correct directory (src/web)

## Running with a Real LLM (Ollama)

To run the system with a real LLM instead of test mode:

1. Install Ollama: https://ollama.com/download
2. Pull a model: `ollama pull tinyllama`
3. Start Ollama: `ollama serve`
4. Start the backend without test mode:
   ```bash
   export PYTHONPATH=$PWD
   cd src/backend
   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Stopping the Servers

To stop the servers:

```bash
# If using the test mode script
pkill -f "uvicorn|http.server"

# Or if you know the PIDs
kill <backend_pid> <web_ui_pid>
```
