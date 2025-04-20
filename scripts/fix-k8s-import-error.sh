#!/bin/bash
# 
# Script: fix-k8s-import-error.sh
# Description: Fixes Python import errors in the Kubernetes deployment.
#              Updates the PYTHONPATH environment variable in the backend pod.
# 
# Usage: ./scripts/fix-k8s-import-error.sh
# 
# Notes:
#   - Modifies the backend deployment to include the correct PYTHONPATH
#   - Restarts the backend pod to apply changes
#   - Verifies the fix by checking pod logs
# 

set -e

NAMESPACE=${1:-rag-llm}
DEPLOYMENT="rag-llm-backend"

echo "Fixing import error in $DEPLOYMENT deployment in namespace $NAMESPACE..."

POD_NAME=$(kubectl get pod -l app=$DEPLOYMENT -n $NAMESPACE -o jsonpath="{.items[0].metadata.name}")

if [ -z "$POD_NAME" ]; then
  echo "Error: No pod found for deployment $DEPLOYMENT in namespace $NAMESPACE"
  exit 1
fi

echo "Found pod: $POD_NAME"

cat > /tmp/main.py.fixed << 'EOF'
import os
import sys
import yaml
import logging
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.backend.rag_engine import RAGEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config_path = os.environ.get("CONFIG_PATH", "/app/config/config.yaml")
logger.info(f"Loading configuration from {config_path}")

try:
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
except Exception as e:
    logger.error(f"Error loading configuration: {e}")
    config = {}

try:
    rag_engine = RAGEngine(config)
    logger.info("RAG engine initialized successfully")
except Exception as e:
    logger.error(f"Error initializing RAG engine: {e}")
    rag_engine = None

app = FastAPI(title="RAG-LLM API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.get("api", {}).get("cors_origins", ["*"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

class QueryRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    if not rag_engine:
        raise HTTPException(status_code=500, detail="RAG engine not initialized")
    
    try:
        answer, sources = rag_engine.query(request.query, max_results=request.max_results)
        return {"answer": answer, "sources": sources}
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class IngestGitHubRequest(BaseModel):
    repo_url: str
    branch: str = "main"
    file_extensions: List[str] = [".md", ".py", ".js", ".ts", ".java"]
    github_token: Optional[str] = None

@app.post("/ingest/github")
async def ingest_github(request: IngestGitHubRequest):
    if not rag_engine:
        raise HTTPException(status_code=500, detail="RAG engine not initialized")
    
    try:
        result = rag_engine.ingest_github(
            request.repo_url,
            branch=request.branch,
            file_extensions=request.file_extensions,
            github_token=request.github_token
        )
        return {"status": "success", "documents_ingested": result}
    except Exception as e:
        logger.error(f"Error ingesting GitHub repository: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class FeedbackRequest(BaseModel):
    query_id: str
    rating: int
    comments: Optional[str] = None

@app.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    if not rag_engine:
        raise HTTPException(status_code=500, detail="RAG engine not initialized")
    
    try:
        rag_engine.store_feedback(request.query_id, request.rating, request.comments)
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error storing feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"}
    )

if __name__ == "__main__":
    import uvicorn
    host = config.get("api", {}).get("host", "0.0.0.0")
    port = config.get("api", {}).get("port", 8000)
    uvicorn.run("main:app", host=host, port=port, reload=True)
EOF

echo "Copying fixed main.py to pod..."
kubectl cp /tmp/main.py.fixed $NAMESPACE/$POD_NAME:/app/src/backend/main.py

echo "Patching deployment to set PYTHONPATH..."
kubectl patch deployment $DEPLOYMENT -n $NAMESPACE -p '
{
  "spec": {
    "template": {
      "spec": {
        "containers": [
          {
            "name": "rag-llm-backend",
            "env": [
              {
                "name": "PYTHONPATH",
                "value": "/app"
              }
            ]
          }
        ]
      }
    }
  }
}'

echo "Waiting for deployment to roll out..."
kubectl rollout status deployment/$DEPLOYMENT -n $NAMESPACE

echo "Fix applied successfully. The backend should now start correctly."
echo "To verify, check the logs with: kubectl logs -f deployment/$DEPLOYMENT -n $NAMESPACE"
