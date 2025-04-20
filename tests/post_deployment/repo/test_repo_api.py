"""
Repository management API tests for the RAG-LLM Framework post-deployment test suite.
"""
from tests.post_deployment.utils.base_test import BaseTest
from tests.post_deployment.utils.config import GITHUB_TOKEN

class ListReposTest(BaseTest):
    """Test listing configured repositories."""
    
    def __init__(self):
        super().__init__(
            name="List Repositories API",
            description="Test listing configured GitHub repositories."
        )
        
    def execute(self):
        success, response = self.request("GET", "/repos")
        return success and "repositories" in response
        
class UpdateReposTest(BaseTest):
    """Test updating repository configuration."""
    
    def __init__(self):
        super().__init__(
            name="Update Repositories API",
            description="Test updating GitHub repository configuration."
        )
        
    def execute(self):
        data = {
            "repositories": [
                {
                    "repo_url": "https://github.com/example/test-repo",
                    "branch": "main",
                    "file_extensions": [".md", ".py"]
                }
            ],
            "auto_ingest_on_startup": False
        }
        success, response = self.request("POST", "/repos/update-config", data)
        return success and response.get("status") == "success"
        
class IngestGitHubTest(BaseTest):
    """Test ingesting a GitHub repository."""
    
    def __init__(self):
        super().__init__(
            name="Ingest GitHub API",
            description="Test ingesting a specific GitHub repository."
        )
        
    def execute(self):
        data = {
            "repo_url": "https://github.com/test-mode/test-repo",
            "branch": "main",
            "file_extensions": [".md"]
        }
        success, response = self.request("POST", "/repos/ingest-github", data)
        
        return success
        
class IngestAllReposTest(BaseTest):
    """Test ingesting all configured repositories."""
    
    def __init__(self):
        super().__init__(
            name="Ingest All Repositories API",
            description="Test ingesting all configured GitHub repositories."
        )
        
    def execute(self):
        success, response = self.request("POST", "/repos/ingest-repos", {})
        return success
        
class RepoConfigTest(BaseTest):
    """Test getting repository configuration."""
    
    def __init__(self):
        super().__init__(
            name="Repository Configuration API",
            description="Test retrieving the current repository configuration."
        )
        
    def execute(self):
        success, response = self.request("GET", "/repos/config")
        return success and "repositories" in response and "auto_ingest_on_startup" in response

repo_tests = [
    ListReposTest(),
    RepoConfigTest(),
    UpdateReposTest(),
    IngestGitHubTest(),
    IngestAllReposTest()
]
