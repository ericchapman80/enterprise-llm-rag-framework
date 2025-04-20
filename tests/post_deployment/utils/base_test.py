"""
Base test class for the RAG-LLM Framework post-deployment tests.
"""
import requests
import json
import logging
import time
import uuid
from datetime import datetime

from tests.post_deployment.utils.config import BASE_URL, TEST_TIMEOUT

logger = logging.getLogger("rag-tests")

class BaseTest:
    """Base class for all RAG-LLM API tests."""
    
    def __init__(self, name, description=""):
        self.name = name
        self.description = description
        self.base_url = BASE_URL
        self.timeout = TEST_TIMEOUT
        self.start_time = None
        self.end_time = None
        self.duration = None
        self.status = "Not Run"
        self.error = None
        self.test_id = str(uuid.uuid4())
        
    def setup(self):
        """Setup before test execution."""
        self.start_time = datetime.now()
        logger.info(f"Starting test: {self.name}")
        
    def teardown(self):
        """Cleanup after test execution."""
        self.end_time = datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()
        logger.info(f"Finished test: {self.name} in {self.duration:.2f}s with status: {self.status}")
        
    def run(self):
        """Run the test and return results."""
        try:
            self.setup()
            result = self.execute()
            self.status = "Pass" if result else "Fail"
        except Exception as e:
            logger.error(f"Error executing test {self.name}: {str(e)}")
            self.status = "Error"
            self.error = str(e)
        finally:
            self.teardown()
            
        return {
            "id": self.test_id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "duration": self.duration,
            "error": self.error,
            "timestamp": self.start_time.isoformat() if self.start_time else None
        }
        
    def execute(self):
        """Execute the test. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement execute method")
        
    def request(self, method, endpoint, data=None, expected_status=200):
        """Helper method to make API requests."""
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method.upper() == "GET":
                response = requests.get(url, timeout=self.timeout)
            elif method.upper() == "POST":
                response = requests.post(
                    url,
                    json=data,
                    headers={"Content-Type": "application/json"},
                    timeout=self.timeout
                )
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            if response.status_code != expected_status:
                logger.error(f"Unexpected status code: {response.status_code} (expected {expected_status})")
                logger.error(f"Response: {response.text[:500]}...")
                return False, None
                
            try:
                if response.text:
                    result = response.json()
                    return True, result
                else:
                    return True, None
            except json.JSONDecodeError:
                if expected_status != 200:
                    return True, None
                logger.error(f"Response is not valid JSON: {response.text[:500]}...")
                return False, None
                
        except requests.exceptions.Timeout:
            logger.error(f"Request timed out: {endpoint}")
            return False, None
        except Exception as e:
            logger.error(f"Error making request to {endpoint}: {str(e)}")
            return False, None
