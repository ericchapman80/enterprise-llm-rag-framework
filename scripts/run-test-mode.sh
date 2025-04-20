# 
# 
# 
# 

set -e

BACKEND_PORT=8000
WEB_UI_PORT=8080

echo "=== Starting RAG-LLM Framework in Test Mode ==="
echo "Note: This mode bypasses Ollama requirements for testing purposes."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

mkdir -p "$PROJECT_ROOT/data/chroma_db"
mkdir -p "$PROJECT_ROOT/src"
mkdir -p "$PROJECT_ROOT/src/backend"
mkdir -p "$PROJECT_ROOT/config"

touch "$PROJECT_ROOT/src/__init__.py"
touch "$PROJECT_ROOT/src/backend/__init__.py"

if [ ! -f "$PROJECT_ROOT/config/config.yaml" ]; then
    echo "Creating default config file..."
    cat > "$PROJECT_ROOT/config/config.yaml" << EOF
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

if [ ! -d "$PROJECT_ROOT/rag-llm-env" ]; then
    echo "Creating Python virtual environment..."
    cd "$PROJECT_ROOT"
    python -m venv rag-llm-env
fi

echo "Activating virtual environment..."
source "$PROJECT_ROOT/rag-llm-env/bin/activate"

echo "Installing backend dependencies..."
pip install -r "$PROJECT_ROOT/src/backend/requirements.txt"
pip install python-multipart

echo "Starting backend API server on port $BACKEND_PORT..."
cd "$PROJECT_ROOT"
export PYTHONPATH="$PROJECT_ROOT"
export RAG_TEST_MODE=true

cat > "$PROJECT_ROOT/src/backend/main_test.py" << EOF
"""
RAG-LLM Framework Backend - Test Mode
This is a simplified version of main.py that works in test mode without Ollama.
"""
import os
import sys
import logging
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RAG-LLM Framework API",
    description="API for the RAG-LLM Framework with GitHub integration and chat capabilities",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    from src.backend.chat_router import router as chat_router
    app.include_router(chat_router, prefix="/chat")
except ImportError as e:
    logger.error(f"Error importing chat_router: {str(e)}")
    from chat_router import router as chat_router
    app.include_router(chat_router, prefix="/chat")

@app.get("/health", tags=["Health"])
async def health_check():
    """Check if the API is running."""
    return {"status": "ok"}

@app.post("/query", tags=["Query"])
async def query(query_text: str):
    """
    Query the RAG system with a question.
    
    Args:
        query_text: The question to ask
        
    Returns:
        The response from the RAG system
    """
    return {
        "query": query_text,
        "response": f"Test response for: {query_text}",
        "sources": []
    }

@app.post("/github/add-repo", tags=["GitHub"])
async def add_github_repo(repo_url: str, branch: str = "main"):
    """Add a GitHub repository to the RAG system."""
    return {"status": "success", "message": f"Added repository {repo_url} (branch: {branch}) in test mode"}

@app.get("/github/repos", tags=["GitHub"])
async def list_github_repos():
    """List all GitHub repositories in the RAG system."""
    return {"repositories": [{"repo_url": "https://github.com/example/repo1", "branch": "main"}]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

cd "$PROJECT_ROOT"
nohup python -m uvicorn src.backend.main_test:app --host 0.0.0.0 --port $BACKEND_PORT > "$PROJECT_ROOT/backend.log" 2>&1 &
BACKEND_PID=$!
echo "Backend server started with PID $BACKEND_PID"

echo "Waiting for backend to start..."
sleep 5

echo "Starting web UI server on port $WEB_UI_PORT..."
cd "$PROJECT_ROOT/src/web"
nohup python -m http.server $WEB_UI_PORT > "$PROJECT_ROOT/web_ui.log" 2>&1 &
WEB_UI_PID=$!
echo "Web UI server started with PID $WEB_UI_PID"

echo ""
echo "=== RAG-LLM Framework is now running in test mode ==="
echo "Backend API: http://localhost:$BACKEND_PORT"
echo "Web UI: http://localhost:$WEB_UI_PORT"
echo ""
echo "API Documentation: http://localhost:$BACKEND_PORT/docs"
echo ""
echo "To stop the servers, run: kill $BACKEND_PID $WEB_UI_PID"
echo "Or use: pkill -f 'uvicorn|http.server'"
echo ""
echo "Backend logs: $PROJECT_ROOT/backend.log"
echo "Web UI logs: $PROJECT_ROOT/web_ui.log"
