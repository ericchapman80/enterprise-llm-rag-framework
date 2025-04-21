"""
Repository management module for the RAG-LLM Framework.
This module provides functionality for managing GitHub repositories to be ingested by the RAG system.
"""
import os
import json
import logging
import random
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import concurrent.futures
import multiprocessing

from src.backend.data_ingestion import DataIngestionManager
from src.backend.rag_engine import RAGEngine, get_rag_engine
from langchain.schema import Document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Repository Management"])

REPOS_CONFIG_PATH = os.environ.get("REPOS_CONFIG_PATH", "config/github_repos.json")

class Repository(BaseModel):
    """Model for a GitHub repository configuration."""
    repo_url: str
    branch: str = "main"
    file_extensions: List[str] = [".md", ".py", ".js", ".txt"]
    description: Optional[str] = None

class RepositoryConfig(BaseModel):
    """Model for the repository configuration file."""
    repositories: List[Repository]
    auto_ingest_on_startup: bool = True
    last_updated: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class UpdateReposRequest(BaseModel):
    """Model for updating the repository list."""
    repositories: List[Repository]
    auto_ingest_on_startup: Optional[bool] = None

class UpdateReposResponse(BaseModel):
    """Model for the response to an update repositories request."""
    status: str
    message: str
    repositories: List[Repository]

def load_repository_config() -> RepositoryConfig:
    """
    Load the repository configuration from the config file.
    Returns:
        The repository configuration
    Raises:
        HTTPException: If the config file is missing or cannot be parsed
    """
    try:
        if not os.path.exists(REPOS_CONFIG_PATH):
            logger.error(f"Repository config file not found at: {REPOS_CONFIG_PATH}")
            raise HTTPException(status_code=500, detail=f"Repository config file not found at: {REPOS_CONFIG_PATH}")
        with open(REPOS_CONFIG_PATH, "r") as f:
            config_data = json.load(f)
        try:
            return RepositoryConfig(**config_data)
        except Exception as e:
            logger.error(f"Error parsing repository configuration: {str(e)}. Raw data: {config_data}")
            raise HTTPException(status_code=500, detail=f"Error parsing repository configuration: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading repository configuration: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error loading repository configuration: {str(e)}")

def save_repository_config(config: RepositoryConfig) -> bool:
    """
    Save the repository configuration to the config file.
    
    Args:
        config: The repository configuration to save
        
    Returns:
        True if the configuration was saved successfully, False otherwise
    """
    try:
        os.makedirs(os.path.dirname(REPOS_CONFIG_PATH), exist_ok=True)
        
        config.last_updated = datetime.utcnow().isoformat()
        
        with open(REPOS_CONFIG_PATH, "w") as f:
            json.dump(config.dict(), f, indent=2)
        
        return True
    except Exception as e:
        logger.error(f"Error saving repository configuration: {str(e)}")
        return False

def get_optimal_thread_count() -> int:
    """
    Determine the optimal number of threads for repository ingestion based on environment.
    
    Returns:
        The optimal number of threads to use
    """
    env_thread_count = os.environ.get("RAG_INGESTION_THREADS")
    if env_thread_count and env_thread_count.isdigit():
        thread_count = int(env_thread_count)
        logger.info(f"🧵 Using {thread_count} threads for repository ingestion (from environment)")
        return thread_count
        
    cpu_count = multiprocessing.cpu_count()
    default_thread_count = max(2, min(cpu_count, 8))
    logger.info(f"🧵 Using {default_thread_count} threads for repository ingestion (auto-detected from {cpu_count} CPU cores)")
    return default_thread_count

async def ingest_repositories(repositories: List[Repository], thread_count: int, rag_engine: RAGEngine) -> List[Dict[str, Any]]:
    """
    Ingest a list of repositories into the RAG system.
    
    Args:
        repositories: The list of repositories to ingest
        thread_count: Number of threads to use for parallel ingestion
        rag_engine: The RAG engine instance
        
    Returns:
        A list of dictionaries containing the ingestion results for each repository
    """
    results = []
    
    if os.environ.get("RAG_TEST_MODE") == "true":
        logger.info("🧪 Running in test mode. Simulating repository ingestion.")
        for repo in repositories:
            doc_count = random.randint(5, 20)
            results.append({
                "repo_url": repo.repo_url,
                "branch": repo.branch,
                "status": "success",
                "message": f"Successfully simulated ingestion of GitHub repository: {repo.repo_url} in test mode",
                "document_count": doc_count
            })
        return results
    
    ingestion_manager = DataIngestionManager()
    github_token = os.environ.get("GITHUB_TOKEN")
    
    if not github_token:
        logger.warning("⚠️ GitHub token not found. Set the GITHUB_TOKEN environment variable for GitHub repository ingestion.")
        for repo in repositories:
            results.append({
                "repo_url": repo.repo_url,
                "branch": repo.branch,
                "status": "failed",
                "error": "GitHub token not provided. Set the GITHUB_TOKEN environment variable."
            })
        return results
    
    def process_repository(repo):
        try:
            logger.info(f"📚 Ingesting repository: {repo.repo_url}, branch: {repo.branch}")
            
            documents = ingestion_manager.ingest_github_repo(
                repo_url=repo.repo_url,
                branch=repo.branch,
                github_token=github_token,
                file_filter=repo.file_extensions
            )
            
            rag_engine.add_documents(documents)
            logger.info(f"✅ Successfully added {len(documents)} documents from {repo.repo_url} to the database")
            
            return {
                "repo_url": repo.repo_url,
                "branch": repo.branch,
                "status": "success",
                "message": f"Successfully ingested {len(documents)} documents from GitHub repository",
                "document_count": len(documents)
            }
        except Exception as e:
            logger.error(f"❌ Error ingesting repository {repo.repo_url}: {str(e)}")
            return {
                "repo_url": repo.repo_url,
                "branch": repo.branch,
                "status": "failed",
                "error": str(e)
            }
    
    logger.info(f"🔄 Processing {len(repositories)} repositories using {thread_count} threads")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
        future_to_repo = {executor.submit(process_repository, repo): repo for repo in repositories}
        
        for future in concurrent.futures.as_completed(future_to_repo):
            result = future.result()
            results.append(result)
            if result.get("status") == "success":
                logger.info(f"📊 Repository {result['repo_url']} successfully added to database with {result['document_count']} documents")
            else:
                logger.error(f"❌ Repository {result['repo_url']} failed: {result.get('error')}")
    
    return results

@router.get(
    "/repos",
    response_model=RepositoryConfig,
    summary="List configured GitHub repositories",
    description="This endpoint returns the list of GitHub repositories configured for ingestion by the RAG system.",
    response_description="The list of configured GitHub repositories"
)
async def list_repositories() -> RepositoryConfig:
    """
    List the GitHub repositories configured for ingestion.
    
    Returns:
        The repository configuration
    """
    try:
        config = load_repository_config()
        return config
    except Exception as e:
        logger.error(f"Error listing repositories: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing repositories: {str(e)}")

@router.post(
    "/repos/ingest-github",
    summary="Ingest a GitHub repository",
    description="This endpoint ingests a GitHub repository into the RAG system.",
    response_description="Status of the repository ingestion operation"
)
async def ingest_github_repo(
    repo: Repository,
    rag_engine: RAGEngine = Depends(get_rag_engine)
) -> Dict[str, Any]:
    """Alias for the /ingest/github endpoint."""
    try:
        if os.environ.get("RAG_TEST_MODE") == "true":
            logger.info(f"🧪 Test mode: Simulating GitHub repository ingestion for: {repo.repo_url}")
            
            import random
            doc_count = random.randint(5, 20)
            
            return {
                "status": "success",
                "message": f"Successfully simulated ingestion of GitHub repository: {repo.repo_url} in test mode",
                "document_count": doc_count
            }
        
        if not repo.repo_url:
            raise HTTPException(status_code=400, detail="Repository URL is required")
        
        github_token = os.environ.get("GITHUB_TOKEN")
        
        logger.info(f"Ingesting GitHub repository: {repo.repo_url}, branch: {repo.branch}")
        
        ingestion_manager = DataIngestionManager()
        
        try:
            documents = ingestion_manager.ingest_github_repo(
                repo_url=repo.repo_url,
                branch=repo.branch,
                github_token=github_token,
                file_filter=repo.file_extensions
            )
            
            rag_engine.add_documents(documents)
            
            return {
                "status": "success", 
                "message": f"Successfully ingested {len(documents)} documents from GitHub repository",
                "document_count": len(documents)
            }
        except Exception as repo_error:
            logger.error(f"Error ingesting GitHub repository: {repo_error}")
            raise HTTPException(status_code=500, detail=f"Error ingesting GitHub repository: {str(repo_error)}")
    
    except Exception as e:
        logger.error(f"Error processing GitHub ingestion request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/repos/ingest-repos",
    summary="Ingest all configured repositories",
    description="This endpoint ingests all repositories configured in the repository configuration file (config/github_repos.json) into the RAG system. It can be used to refresh the knowledge base with the latest content from all configured repositories.",
    response_description="Status of the repository ingestion operation with detailed success/failure information"
)
async def ingest_all_repositories(
    rag_engine: RAGEngine = Depends(get_rag_engine)
) -> Dict[str, Any]:
    """
    Ingest all repositories configured in the repository configuration file.
    
    This endpoint will:
    1. Read the repository configuration from config/github_repos.json
    2. Attempt to ingest all configured repositories
    3. Return detailed success/failure status for each repository
    
    This endpoint is useful for refreshing the RAG system's knowledge base with the latest content
    from all configured GitHub repositories. It can be called via a cron job using the provided
    scripts/refresh-github-repos.sh script.
    
    Environment Variables:
        GITHUB_TOKEN: GitHub personal access token for accessing repositories
    
    Args:
        rag_engine: The RAG engine instance
        
    Returns:
        Dict[str, Any]: Status of the ingestion process for each repository, including:
            - success/failure counts
            - list of successfully ingested repositories with document counts
            - list of failed repositories with error messages
    
    Raises:
        HTTPException(500): If there's an error reading the configuration or processing repositories
    """
    if os.environ.get("RAG_TEST_MODE") == "true":
        logger.info("🧪 Running in test mode. Simulating repository ingestion.")
        
        results = []
        for i in range(2):
            repo_name = f"example/repo{i+1}"
            doc_count = random.randint(5, 20)
            results.append({
                "repo_url": f"https://github.com/{repo_name}",
                "branch": "main",
                "status": "success",
                "message": f"Successfully simulated ingestion of GitHub repository in test mode",
                "document_count": doc_count
            })
        
        success_count = sum(1 for r in results if r.get("status") == "success")
        failed_count = len(results) - success_count
        
        return {
            "status": "success",
            "message": f"Ingestion completed with {success_count} successful and {failed_count} failed repositories (test mode)",
            "results": results
        }
    
    try:
        config = load_repository_config()
        
        # Determine optimal thread count
        thread_count = get_optimal_thread_count()
        
        # Ingest repositories with multithreading
        results = await ingest_repositories(config.repositories, thread_count, rag_engine)
        
        success_count = sum(1 for r in results if r.get("status") == "success")
        failed_count = len(results) - success_count
        
        return {
            "status": "success",
            "message": f"Ingestion completed with {success_count} successful and {failed_count} failed repositories",
            "results": results
        }
    except Exception as e:
        logger.error(f"Error ingesting repositories: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error ingesting repositories: {str(e)}")

@router.post(
    "/repos/update-config",
    response_model=UpdateReposResponse,
    summary="Update repository configuration",
    description="This endpoint updates the repository configuration with the provided repositories and settings.",
    response_description="Status of the configuration update operation"
)
async def update_repository_config(request: UpdateReposRequest) -> Dict[str, Any]:
    """
    Update the repository configuration.
    
    Args:
        request: The update request
    """
    try:
        config = load_repository_config()
        
        config.repositories = request.repositories
        
        if request.auto_ingest_on_startup is not None:
            config.auto_ingest_on_startup = request.auto_ingest_on_startup
        
        if not save_repository_config(config):
            raise HTTPException(status_code=500, detail="Failed to save repository configuration")
        
        return {
            "status": "success",
            "message": f"Successfully updated repository configuration with {len(request.repositories)} repositories",
            "repositories": config.repositories
        }
    except Exception as e:
        logger.error(f"Error updating repository configuration: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating repository configuration: {str(e)}")

async def ingest_repositories_on_startup(rag_engine: RAGEngine) -> None:
    """
    Ingest repositories on startup if auto_ingest_on_startup is enabled.
    
    Args:
        rag_engine: The RAG engine instance
    """
    try:
        if os.environ.get("RAG_TEST_MODE") == "true":
            logger.info("🧪 Skipping auto-ingestion in test mode")
            return
            
        config = load_repository_config()
        
        if not config.auto_ingest_on_startup:
            logger.info("ℹ️ Auto-ingestion of repositories is disabled")
            return
        
        if not config.repositories:
            logger.info("ℹ️ No repositories configured for ingestion")
            return
        
        logger.info(f"🚀 Auto-ingesting {len(config.repositories)} repositories on startup")
        
        for idx, repo in enumerate(config.repositories):
            logger.info(f"📋 Repository {idx+1}/{len(config.repositories)}: {repo.repo_url} (branch: {repo.branch})")
        
        # Determine optimal thread count
        thread_count = get_optimal_thread_count()
        results = await ingest_repositories(config.repositories, thread_count, rag_engine)
        
        success_count = sum(1 for r in results if r.get("status") == "success")
        failed_count = len(results) - success_count
        
        logger.info(f"✅ Successfully ingested {success_count} repositories into the database")
        if failed_count > 0:
            logger.warning(f"⚠️ Failed to ingest {failed_count} repositories")
            
        # Log total document count
        total_docs = sum(r.get("document_count", 0) for r in results if r.get("status") == "success")
        logger.info(f"📚 Total documents added to database: {total_docs}")
        
    except Exception as e:
        logger.error(f"❌ Error ingesting repositories on startup: {str(e)}")
