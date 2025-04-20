"""
Core API tests for the RAG-LLM Framework post-deployment test suite.
"""
from tests.post_deployment.utils.base_test import BaseTest
from tests.post_deployment.utils.config import TEST_QUERY, TEST_FEEDBACK

class HealthCheckTest(BaseTest):
    """Test the health check endpoint."""
    
    def __init__(self):
        super().__init__(
            name="Health Check",
            description="Verify the API health endpoint is working correctly."
        )
        
    def execute(self):
        success, response = self.request("GET", "/health")
        return success and response.get("status") == "healthy"
        
class QueryTest(BaseTest):
    """Test the query endpoint."""
    
    def __init__(self):
        super().__init__(
            name="Query API",
            description="Test querying the RAG system with a natural language prompt."
        )
        
    def execute(self):
        data = {"query": TEST_QUERY}
        success, response = self.request("POST", "/query", data)
        return success and "response" in response and "sources" in response
        
class FeedbackTest(BaseTest):
    """Test the feedback endpoint."""
    
    def __init__(self):
        super().__init__(
            name="Feedback API",
            description="Test submitting feedback for a query response."
        )
        
    def execute(self):
        data = {
            "query_id": "test-query-id",
            "feedback": TEST_FEEDBACK,
            "rating": 5,
            "details": "Automated test feedback"
        }
        success, response = self.request("POST", "/feedback", data)
        return success and response.get("status") == "success"
        
class IngestTest(BaseTest):
    """Test the data ingestion endpoint."""
    
    def __init__(self):
        super().__init__(
            name="Ingest API",
            description="Test ingesting text data into the RAG system."
        )
        
    def execute(self):
        data = {
            "source_type": "text",
            "source_data": "This is a test document for the post-deployment test suite.",
            "metadata": {"source": "post-deployment-test"}
        }
        success, response = self.request("POST", "/ingest", data)
        return success and response.get("status") == "success"
        
class IngestedDataTest(BaseTest):
    """Test the ingested data endpoint."""
    
    def __init__(self):
        super().__init__(
            name="Ingested Data API",
            description="Test retrieving the list of ingested documents."
        )
        
    def execute(self):
        success, response = self.request("GET", "/ingested-data")
        return success and "documents" in response
        
class QueryComparisonTest(BaseTest):
    """Test the query comparison endpoint."""
    
    def __init__(self):
        super().__init__(
            name="Query Comparison API",
            description="Test comparing RAG and non-RAG responses."
        )
        
    def execute(self):
        data = {"query": TEST_QUERY}
        success, response = self.request("POST", "/query-comparison", data)
        return (success and 
               "query" in response and 
               ("with_rag" in response or "rag_response" in response))

core_tests = [
    HealthCheckTest(),
    QueryTest(),
    FeedbackTest(),
    IngestTest(),
    IngestedDataTest(),
    QueryComparisonTest()
]
