"""
Data ingestion module for the RAG-enabled LLM system.
"""
import os
import logging
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import tempfile
import shutil
from github import Github
from langchain_community.document_loaders import (
    TextLoader, 
    UnstructuredMarkdownLoader,
    DirectoryLoader,
    GitLoader
)
from langchain.schema import Document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataIngestionManager:
    """
    Manager for ingesting data from various sources into the RAG system.
    """
    
    def __init__(self):
        """Initialize the data ingestion manager."""
        pass
    
    def ingest_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Document]:
        """
        Ingest raw text.
        
        Args:
            text: The text content
            metadata: Optional metadata about the text
            
        Returns:
            List of Document objects
        """
        try:
            if metadata is None:
                metadata = {}
            
            document = Document(page_content=text, metadata=metadata)
            logger.info(f"Ingested text with metadata: {metadata}")
            return [document]
        except Exception as e:
            logger.error(f"Error ingesting text: {str(e)}")
            raise
    
    def ingest_markdown_file(self, file_path: Union[str, Path], metadata: Optional[Dict[str, Any]] = None) -> List[Document]:
        """
        Ingest a markdown file.
        
        Args:
            file_path: Path to the markdown file
            metadata: Optional metadata about the file
            
        Returns:
            List of Document objects
        """
        try:
            if metadata is None:
                metadata = {}
            
            loader = UnstructuredMarkdownLoader(str(file_path), metadata=metadata)
            documents = loader.load()
            logger.info(f"Ingested markdown file: {file_path}")
            return documents
        except Exception as e:
            logger.error(f"Error ingesting markdown file: {str(e)}")
            raise
    
    def ingest_text_file(self, file_path: Union[str, Path], metadata: Optional[Dict[str, Any]] = None) -> List[Document]:
        """
        Ingest a text file.
        
        Args:
            file_path: Path to the text file
            metadata: Optional metadata about the file
            
        Returns:
            List of Document objects
        """
        try:
            if metadata is None:
                metadata = {}
            
            loader = TextLoader(str(file_path), metadata=metadata)
            documents = loader.load()
            logger.info(f"Ingested text file: {file_path}")
            return documents
        except Exception as e:
            logger.error(f"Error ingesting text file: {str(e)}")
            raise
    
    def ingest_directory(self, dir_path: Union[str, Path], glob: str = "**/*.*") -> List[Document]:
        """
        Ingest all files in a directory.
        
        Args:
            dir_path: Path to the directory
            glob: Glob pattern for files to include
            
        Returns:
            List of Document objects
        """
        try:
            loader = DirectoryLoader(
                str(dir_path),
                glob=glob,
                loader_cls=TextLoader
            )
            documents = loader.load()
            logger.info(f"Ingested {len(documents)} files from directory: {dir_path}")
            return documents
        except Exception as e:
            logger.error(f"Error ingesting directory: {str(e)}")
            raise
    
    def ingest_github_repo(
        self, 
        repo_url: str, 
        branch: str = "main",
        github_token: Optional[str] = None,
        file_filter: Optional[List[str]] = None
    ) -> List[Document]:
        """
        Ingest a GitHub repository.
        
        Args:
            repo_url: URL of the GitHub repository
            branch: Branch to clone
            github_token: Optional GitHub token for private repos
            file_filter: Optional list of file extensions to include
            
        Returns:
            List of Document objects
        """
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                if github_token:
                    g = Github(github_token)
                    repo_name = repo_url.split('/')[-2] + '/' + repo_url.split('/')[-1]
                    repo = g.get_repo(repo_name)
                    
                    loader = GitLoader(
                        clone_url=repo_url,
                        repo_path=temp_dir,
                        branch=branch
                    )
                else:
                    loader = GitLoader(
                        clone_url=repo_url,
                        repo_path=temp_dir,
                        branch=branch
                    )
                
                documents = loader.load()
                
                if file_filter:
                    filtered_docs = []
                    for doc in documents:
                        file_ext = Path(doc.metadata.get("source", "")).suffix
                        if file_ext in file_filter:
                            filtered_docs.append(doc)
                    documents = filtered_docs
                
                logger.info(f"Ingested {len(documents)} files from GitHub repo: {repo_url}")
                return documents
        except Exception as e:
            logger.error(f"Error ingesting GitHub repo: {str(e)}")
            raise
