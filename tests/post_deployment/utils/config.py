"""
Configuration module for the RAG-LLM Framework post-deployment tests.
"""
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("rag-tests")

BASE_URL = os.environ.get("RAG_API_URL", "http://localhost:8000")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "test-token-for-testing")
TEST_TIMEOUT = int(os.environ.get("TEST_TIMEOUT", "30"))
PARALLEL_TESTS = int(os.environ.get("PARALLEL_TESTS", "4"))
REPORT_FORMAT = os.environ.get("REPORT_FORMAT", "html,json")

os.environ["RAG_TEST_MODE"] = "true"

TEST_QUERY = "What is RAG?"
TEST_CHAT_MESSAGE = "How can you help me with GitHub repositories?"
TEST_FEEDBACK = "This response was very helpful."
