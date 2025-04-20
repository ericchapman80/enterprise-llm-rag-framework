"""
Repository management module for the RAG-LLM Framework.
This module provides functionality for managing GitHub repositories to be ingested by the RAG system.
"""
import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from src.backend.data_ingestion import DataIngestionManager
from src.backend.rag_engine import RAGEngine

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
    """
    try:
        if not os.path.exists(REPOS_CONFIG_PATH):
            default_config = RepositoryConfig(repositories=[])
            save_repository_config(default_config)
            return default_config
        
        with open(REPOS_CONFIG_PATH, "r") as f:
            config_data = json.load(f)
        
        return RepositoryConfig(**config_data)
    except Exception as e:
        logger.error(f"Error loading repository configuration: {str(e)}")
        return RepositoryConfig(repositories=[])

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

async def ingest_repositories(repositories: List[Repository], rag_engine: RAGEngine) -> Dict[str, Any]:
    """
    Ingest a list of repositories into the RAG system.
    
    Args:
        repositories: The list of repositories to ingest
        rag_engine: The RAG engine instance
        
    Returns:
        A dictionary containing the ingestion results
    """
    results = {
        "success": [],
        "failed": []
    }
    
    ingestion_manager = DataIngestionManager()
    github_token = os.environ.get("GITHUB_TOKEN")
    
    if not github_token and os.environ.get("RAG_TEST_MODE") != "true":
        logger.warning("GitHub token not found. Set the GITHUB_TOKEN environment variable for GitHub repository ingestion.")
        for repo in repositories:
            results["failed"].append({
                "repo_url": repo.repo_url,
                "branch": repo.branch,
                "error": "GitHub token not provided. Set the GITHUB_TOKEN environment variable."
            })
        return results
    
    if os.environ.get("RAG_TEST_MODE") == "true":
        logger.info("Running in test mode. Simulating repository ingestion.")
        for repo in repositories:
            if "example" in repo.repo_url or "test" in repo.repo_url:
                results["success"].append({
                    "repo_url": repo.repo_url,
                    "branch": repo.branch,
                    "document_count": 5  # Simulated document count
                })
            else:
                results["failed"].append({
                    "repo_url": repo.repo_url,
                    "branch": repo.branch,
                    "error": "Authentication failed in test mode"
                })
        return results
    
    for repo in repositories:
        try:
            logger.info(f"Ingesting repository: {repo.repo_url}, branch: {repo.branch}")
            
            documents = ingestion_manager.ingest_github_repo(
                repo_url=repo.repo_url,
                branch=repo.branch,
                github_token=github_token,
                file_filter=repo.file_extensions
            )
            
            rag_engine.add_documents(documents)
            
            results["success"].append({
                "repo_url": repo.repo_url,
                "branch": repo.branch,
                "document_count": len(documents)
            })
        except Exception as e:
            logger.error(f"Error ingesting repository {repo.repo_url}: {str(e)}")
            results["failed"].append({
                "repo_url": repo.repo_url,
                "branch": repo.branch,
                "error": str(e)
            })
    
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
    "/update-repos",
    response_model=UpdateReposResponse,
    summary="Update GitHub repository list",
    description="Update the list of GitHub repositories to be ingested by the RAG system. This endpoint allows adding, removing, or modifying repositories in the configuration file.",
    response_description="Status of the repository update operation"
)
async def update_repos(
    request: UpdateReposRequest
) -> Dict[str, Any]:
    """
    Update the list of GitHub repositories to be ingested.
    
    Args:
        request: The update request containing the repositories to add, remove, or modify
        
    Returns:
        A dictionary containing the status of the operation and the updated repository list
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

@router.post(
    "/ingest/github",
    summary="Ingest a GitHub repository into the RAG system",
    description="This endpoint allows ingestion of a GitHub repository into the RAG system. The repository contents will be processed, embedded, and stored in the vector database for retrieval during queries.",
    response_description="Status of the GitHub repository ingestion operation"
)
async def ingest_github_repository(
    repo: Repository,
    rag_engine: RAGEngine = Depends(lambda: RAGEngine(config={}))
) -> Dict[str, Any]:
    """
    Ingest a GitHub repository into the RAG system.
    
    Args:
        repo: The repository to ingest
        rag_engine: The RAG engine instance
        
    Returns:
        A dictionary containing the ingestion results
    """
    try:
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
    description="This endpoint ingests all repositories configured in the repository configuration file into the RAG system.",
    response_description="Status of the repository ingestion operation"
)
async def ingest_all_repositories(
    rag_engine: RAGEngine = Depends(lambda: RAGEngine(config={}))
) -> Dict[str, Any]:
    """
    Ingest all repositories configured in the repository configuration file.
    
    Args:
        rag_engine: The RAG engine instance
        
    Returns:
        A dictionary containing the ingestion results
    """
    try:
        config = load_repository_config()
        
        results = await ingest_repositories(config.repositories, rag_engine)
        
        return {
            "status": "success",
            "message": f"Ingestion completed with {len(results['success'])} successful and {len(results['failed'])} failed repositories",
            "results": results
        }
    except Exception as e:
        logger.error(f"Error ingesting repositories: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error ingesting repositories: {str(e)}")

async def ingest_repositories_on_startup(rag_engine: RAGEngine) -> None:
    """
    Ingest repositories on startup if auto_ingest_on_startup is enabled.
    
    Args:
        rag_engine: The RAG engine instance
    """
    try:
        if os.environ.get("RAG_TEST_MODE") == "true":
            logger.info("Skipping auto-ingestion in test mode")
            return
            
        config = load_repository_config()
        
        if not config.auto_ingest_on_startup:
            logger.info("Auto-ingestion of repositories is disabled")
            return
        
        if not config.repositories:
            logger.info("No repositories configured for ingestion")
            return
        
        logger.info(f"Auto-ingesting {len(config.repositories)} repositories on startup")
        await ingest_repositories(config.repositories, rag_engine)
    except Exception as e:
        logger.error(f"Error ingesting repositories on startup: {str(e)}")
