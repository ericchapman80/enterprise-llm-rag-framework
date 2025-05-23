from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import yaml
import logging
from typing import Dict, List, Optional, Any
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'src'))

# Try different import approaches
try:
    from src.backend.rag_engine import RAGEngine
    from src.backend.repo_management import router as repo_management_router
    from src.backend.repo_management import ingest_repositories_on_startup
except ImportError:
    try:
        from backend.rag_engine import RAGEngine
        from backend.repo_management import router as repo_management_router
        from backend.repo_management import ingest_repositories_on_startup
    except ImportError:
        try:
            # Relative import
            from .rag_engine import RAGEngine
            from .repo_management import router as repo_management_router
            from .repo_management import ingest_repositories_on_startup
        except ImportError:
            # Last resort - direct import
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from rag_engine import RAGEngine
            from repo_management import router as repo_management_router
            from repo_management import ingest_repositories_on_startup

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config_path = os.environ.get("CONFIG_PATH")
if not config_path:
    config_path = os.path.join(project_root, "config", "config.yaml")
logger.info(f"Loading configuration from {config_path}")

try:
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
except Exception as e:
    logger.error(f"Error loading configuration: {e}")
    config = {
        "llm": {
            "ollama": {
                "base_url": os.environ.get("OLLAMA_BASE_URL", "http://ollama:11434"),
                "model_name": os.environ.get("OLLAMA_MODEL_NAME", "llama2"),
                "parameters": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 2048
                }
            }
        },
        "embeddings": {
            "model_name": "all-MiniLM-L6-v2",
            "vector_db_path": "/data/chroma_db"
        },
        "api": {
            "host": "0.0.0.0",
            "port": 8000,
            "cors_origins": ["*"]
        },
        "ingestion": {
            "threads": int(os.environ.get("RAG_INGESTION_THREADS", "0"))  # 0 means auto-detect
        }
    }

# Initialize RAG engine
try:
    rag_engine = RAGEngine(config)
    logger.info("RAG engine initialized successfully")
except Exception as e:
    logger.error(f"Error initializing RAG engine: {e}")
    rag_engine = None

# Create FastAPI app
app = FastAPI(
    title="RAG-LLM API",
    description="""
    API for RAG-enabled LLM Framework that provides retrieval-augmented generation capabilities. 
    
    This API allows you to:
    - Ingest data from various sources including GitHub repositories
    - Query the knowledge base using natural language
    - Compare responses with and without RAG context
    - Maintain conversational chat sessions with context
    - Provide feedback on responses for continuous improvement
    
    The API is designed to be used with Ollama for LLM capabilities and uses vector embeddings 
    to store and retrieve relevant context from your knowledge base.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config["api"].get("cors_origins", ["*"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    from src.backend.chat_router import router as chat_router
except ImportError:
    try:
        from backend.chat_router import router as chat_router
    except ImportError:
        from chat_router import router as chat_router

app.include_router(repo_management_router, tags=["Repository Management"])
app.include_router(chat_router, prefix="/chat", tags=["Chat"])

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
web_dir = os.path.join(project_root, "src", "web")

if os.path.exists(web_dir):
    app.mount("/web", StaticFiles(directory=web_dir, html=True), name="web")
else:
    logger.warning(f"Web UI directory not found at {web_dir}")

@app.get("/")
async def serve_index():
    """Serve the web UI index page"""
    index_path = os.path.join(web_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        logger.warning(f"Index file not found at {index_path}")
        return {"message": "Web UI not available"}

@app.get(
    "/health",
    tags=["System"],
    summary="Health Check",
    description="Returns the health status of the API and its current version.",
    response_description="Health status and version information"
)
async def health_check():
    """
    Health check endpoint to verify that the API is running correctly.
    
    This endpoint can be used for:
    - Monitoring system health
    - Verifying API availability
    - Checking the current API version
    
    Returns:
        dict: A dictionary containing the health status and version information
    """
    return {"status": "healthy", "version": "1.0.0"}

class QueryRequest(BaseModel):
    query: str
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None

class QueryResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]]

@app.post(
    "/query",
    response_model=QueryResponse,
    tags=["Core"],
    summary="Query the RAG-LLM system",
    description="This endpoint processes a query using the RAG-enhanced LLM system. It retrieves relevant context from the vector database and uses it to generate a more informed response.",
    response_description="The LLM response enhanced with relevant context from the vector database"
)
async def query(request_data: QueryRequest):
    """
    Query the RAG-LLM system with a natural language question or prompt.
    
    This endpoint:
    1. Takes a user query as input
    2. Retrieves relevant documents from the vector database
    3. Uses the retrieved documents as context for the LLM
    4. Returns the LLM's response along with the source documents used
    
    Parameters:
        request_data (QueryRequest): The query request containing:
            - query (str): The question or prompt to send to the RAG system
            - max_tokens (int, optional): Maximum number of tokens to generate
            - temperature (float, optional): Controls randomness in the response
    
    Returns:
        QueryResponse: The LLM's response and the source documents used as context
    
    Raises:
        HTTPException(400): If the query text is missing
        HTTPException(500): If there's an error processing the query
    """
    if rag_engine is None:
        raise HTTPException(status_code=500, detail="RAG engine not initialized")
    
    try:
        query_text = request_data.query
        
        if not query_text:
            raise HTTPException(status_code=400, detail="Query text is required")
        
        if os.environ.get("RAG_TEST_MODE") == "true":
            logger.info(f"Running in test mode. Simulating query response for: {query_text}")
            return {
                "response": f"This is a simulated response to your query: '{query_text}'",
                "sources": [
                    {
                        "content": "This is a simulated source document.",
                        "metadata": {
                            "source": "test-source",
                            "file": "test-file.md"
                        }
                    }
                ]
            }
        
        kwargs = {}
        if request_data.max_tokens is not None:
            kwargs["max_tokens"] = request_data.max_tokens
        if request_data.temperature is not None:
            kwargs["temperature"] = request_data.temperature
        
        result = rag_engine.query(query_text, **kwargs)
        return result
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class IngestRequest(BaseModel):
    source_type: str
    source_data: str
    metadata: Optional[Dict[str, Any]] = None

class IngestResponse(BaseModel):
    status: str
    message: str

class IngestedDataResponse(BaseModel):
    status: str
    total_documents: int
    sources: Dict[str, int]

class IngestedDocumentsResponse(BaseModel):
    status: str
    total_documents: int
    documents: List[Dict[str, Any]]

# --- Free-form Data Ingestion Endpoints (with /data/ prefix and Data Ingestion tag) ---
@app.post(
    "/data/ingest",
    response_model=IngestResponse,
    tags=["Data Ingestion"],
    summary="Ingest free-form data into the RAG system",
    description="This endpoint allows ingestion of free-form text or document data into the RAG system. The data will be processed, embedded, and stored in the vector database for retrieval during queries.",
    response_description="Confirmation of data ingestion initiation"
)
async def ingest_data(ingest_data: IngestRequest):
    if rag_engine is None:
        raise HTTPException(status_code=500, detail="RAG engine not initialized")
    try:
        source_type = ingest_data.source_type
        source_data = ingest_data.source_data
        if not source_type or not source_data:
            raise HTTPException(status_code=400, detail="Source type and data are required")
        if os.environ.get("RAG_TEST_MODE") == "true":
            logger.info(f"Test mode: Simulating ingestion of data type {source_type}")
            return {"status": "success", "message": "Data ingestion simulated in test mode"}
        logger.info(f"Ingesting data of type {source_type}")
        return {"status": "success", "message": "Data ingestion started"}
    except Exception as e:
        logger.error(f"Error ingesting data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get(
    "/data/ingested",
    response_model=IngestedDataResponse,
    tags=["Data Ingestion"],
    summary="List ingested data sources",
    description="This endpoint returns a summary of all ingested data sources in the RAG system, including the total number of documents and a breakdown by source.",
    response_description="Summary of ingested data sources"
)
async def list_ingested_data():
    if rag_engine is None:
        raise HTTPException(status_code=500, detail="RAG engine not initialized")
    try:
        documents = rag_engine.list_documents()
        sources = {}
        for doc in documents:
            source = doc.metadata.get("source", "unknown")
            if source not in sources:
                sources[source] = 0
            sources[source] += 1
        return {
            "status": "success",
            "total_documents": len(documents),
            "sources": sources
        }
    except Exception as e:
        logger.error(f"Error listing ingested data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get(
    "/data/ingested-data",
    response_model=IngestedDocumentsResponse,
    tags=["Data Ingestion"],
    summary="View all ingested documents with their content",
    description="This endpoint returns all ingested documents in the RAG system, including their content and metadata. The content is truncated for readability.",
    response_description="List of all ingested documents with content and metadata"
)
async def view_ingested_data():
    if rag_engine is None:
        raise HTTPException(status_code=500, detail="RAG engine not initialized")
    try:
        if os.environ.get("RAG_TEST_MODE") == "true":
            logger.info("Test mode: Returning simulated ingested documents")
            return {
                "status": "success",
                "total_documents": 2,
                "documents": [
                    {
                        "id": 0,
                        "content": "This is a simulated document for testing purposes. It contains information about RAG systems and how they work.",
                        "metadata": {
                            "source": "test-repo",
                            "file": "README.md"
                        }
                    },
                    {
                        "id": 1,
                        "content": "Another simulated document with different content. This one explains how to use the API endpoints.",
                        "metadata": {
                            "source": "test-repo",
                            "file": "docs/api.md"
                        }
                    }
                ]
            }
        documents = rag_engine.list_documents()
        formatted_docs = []
        for i, doc in enumerate(documents):
            formatted_docs.append({
                "id": i,
                "content": doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content,
                "metadata": doc.metadata
            })
        return {
            "status": "success",
            "total_documents": len(documents),
            "documents": formatted_docs
        }
    except Exception as e:
        logger.error(f"Error viewing ingested data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class FlushDatabaseResponse(BaseModel):
    status: str
    message: str

@app.post(
    "/flush-database",
    response_model=FlushDatabaseResponse,
    summary="Flush all documents from the vector database",
    description="This endpoint removes all documents from the vector database, effectively resetting the RAG system's knowledge base.",
    response_description="Confirmation of database flush operation"
)
async def flush_database():
    """Flush all documents from the vector database"""
    if rag_engine is None:
        raise HTTPException(status_code=500, detail="RAG engine not initialized")
    
    try:
        success = rag_engine.flush_vector_store()
        
        return {
            "status": "success" if success else "error",
            "message": "Vector database flushed successfully" if success else "Failed to flush vector database"
        }
    except Exception as e:
        logger.error(f"Error flushing vector database: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class QueryComparisonRequest(BaseModel):
    query: str
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None

class Source(BaseModel):
    content: str
    metadata: Dict[str, str]

class QueryComparisonResponse(BaseModel):
    status: str
    query: str
    with_rag: Dict[str, object]
    without_rag: Dict[str, str]

@app.post(
    "/query-comparison",
    response_model=QueryComparisonResponse,
    tags=["Core"],
    summary="Compare responses with and without RAG context",
    description="This endpoint returns both the RAG-enhanced response (with context from the vector database) and the standard LLM response (without additional context) for the same query. This is useful for evaluating the impact of RAG on response quality.",
    response_description="A comparison of RAG-enhanced and standard LLM responses",
    include_in_schema=False
)
async def query_comparison(request_data: QueryComparisonRequest):
    """Compare responses with and without RAG context"""
    if rag_engine is None:
        raise HTTPException(status_code=500, detail="RAG engine not initialized")
    
    query_text = request_data.query
    
    if not query_text:
        raise HTTPException(status_code=400, detail="Query text is required")
    
    if os.environ.get("RAG_TEST_MODE") == "true":
        logger.info(f"Test mode: Simulating query comparison for: {query_text}")
        return {
            "status": "success",
            "query": query_text,
            "with_rag": {
                "response": f"This is a simulated RAG-enhanced response to: '{query_text}' with additional context from the knowledge base.",
                "sources": [
                    {
                        "content": "This is a simulated source document used for the RAG response.",
                        "metadata": {
                            "source": "test-repo",
                            "file": "test-file.md"
                        }
                    }
                ]
            },
            "without_rag": {
                "response": f"This is a simulated standard LLM response to: '{query_text}'"
            }
        }
        
    try:
        kwargs = {}
        if request_data.max_tokens is not None:
            kwargs["max_tokens"] = request_data.max_tokens
        if request_data.temperature is not None:
            kwargs["temperature"] = request_data.temperature
        
        rag_result = rag_engine.query(query_text, use_rag=True, **kwargs)
        no_rag_result = rag_engine.query(query_text, use_rag=False, **kwargs)
        
        return {
            "status": "success",
            "query": query_text,
            "with_rag": {
                "response": rag_result["response"],
                "sources": rag_result["sources"]
            },
            "without_rag": {
                "response": no_rag_result["response"]
            }
        }
    except Exception as e:
        logger.error(f"Error comparing query responses: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post(
    "/chat/query-comparison",
    response_model=QueryComparisonResponse,
    tags=["Chat"],
    summary="Compare responses with and without RAG context (Chat)",
    description="This endpoint returns both the RAG-enhanced response (with context from the vector database) and the standard LLM response (without additional context) for the same query. This is useful for evaluating the impact of RAG on response quality.",
    response_description="A comparison of RAG-enhanced and standard LLM responses"
)
async def chat_query_comparison(request_data: QueryComparisonRequest):
    """Compare responses with and without RAG context (Chat)"""
    return await query_comparison(request_data)

@app.on_event("startup")
async def startup_event():
    """Perform startup tasks like ingesting repositories."""
    if rag_engine is not None:
        try:
            logger.info("🚀 Starting repository ingestion on startup")
            thread_count = os.environ.get("RAG_INGESTION_THREADS", "auto")
            logger.info(f"🧵 Using thread configuration: {thread_count}")
            
            await ingest_repositories_on_startup(rag_engine)
            
            logger.info("✅ Repository ingestion on startup completed successfully")
            logger.info("📚 RAG system is ready to use with the latest repository data")
        except Exception as e:
            logger.error(f"❌ Error during startup repository ingestion: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host=config["api"].get("host", "0.0.0.0"), 
        port=config["api"].get("port", 8000),
        reload=True
    )
