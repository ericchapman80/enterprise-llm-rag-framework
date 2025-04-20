"""
Test script for multi-threaded repository ingestion.
"""
import os
import sys
import time
import logging
import asyncio
from typing import List, Dict, Any

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'src'))

from src.backend.rag_engine import RAGEngine
from src.backend.repo_management import Repository, ingest_repositories

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_multi_threading():
    """
    Test the multi-threaded repository ingestion functionality.
    """
    config = {
        "llm": {
            "ollama": {
                "base_url": "http://localhost:11434",
                "model_name": "llama2"
            }
        },
        "embeddings": {
            "model_name": "all-MiniLM-L6-v2",
            "vector_db_path": "/tmp/test_chroma_db"
        }
    }
    rag_engine = RAGEngine(config)

    test_repos = [
        Repository(
            repo_url="https://github.com/example/repo1",
            branch="main",
            file_extensions=[".md", ".py"],
            description="Test repository 1"
        ),
        Repository(
            repo_url="https://github.com/example/repo2",
            branch="main",
            file_extensions=[".md", ".py"],
            description="Test repository 2"
        ),
        Repository(
            repo_url="https://github.com/example/repo3",
            branch="main",
            file_extensions=[".md", ".py"],
            description="Test repository 3"
        ),
        Repository(
            repo_url="https://github.com/example/repo4",
            branch="main",
            file_extensions=[".md", ".py"],
            description="Test repository 4"
        )
    ]

    os.environ["RAG_TEST_MODE"] = "true"

    thread_counts = [1, 2, 4]
    for thread_count in thread_counts:
        os.environ["RAG_INGESTION_THREADS"] = str(thread_count)
        logger.info(f"Testing with {thread_count} threads")

        start_time = time.time()
        results = await ingest_repositories(test_repos, rag_engine)
        end_time = time.time()

        logger.info(f"Ingestion completed in {end_time - start_time:.2f} seconds")
        logger.info(f"Successful: {len(results['success'])}, Failed: {len(results['failed'])}")

if __name__ == "__main__":
    asyncio.run(test_multi_threading())
