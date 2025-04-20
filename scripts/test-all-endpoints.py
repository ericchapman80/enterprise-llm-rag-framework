#!/usr/bin/env python3
"""
Test script for all API endpoints in the RAG-LLM Framework.
"""
import requests
import json
import sys
import os
import time
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8000"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "test-token-for-testing")

def check_api_running():
    """Check if the API is running."""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API is running")
            return True
        else:
            print(f"❌ API returned status code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ API is not running")
        return False

def test_endpoint(method, endpoint, data=None, expected_status=200, timeout=5, description=""):
    """Test an API endpoint."""
    print(f"\n--- Testing {method} {endpoint} ---")
    if description:
        print(f"Description: {description}")
    
    try:
        if method.upper() == "GET":
            response = requests.get(
                f"{BASE_URL}{endpoint}",
                timeout=timeout
            )
        elif method.upper() == "POST":
            response = requests.post(
                f"{BASE_URL}{endpoint}",
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=timeout
            )
        else:
            print(f"❌ Unsupported method: {method}")
            return False
        
        print(f"Status code: {response.status_code} (Expected: {expected_status})")
        
        if response.status_code == expected_status:
            try:
                if response.text:
                    result = response.json()
                    print(f"Response: {json.dumps(result, indent=2)[:500]}...")
                else:
                    print("Empty response")
                print("✅ Endpoint test passed")
                return True
            except json.JSONDecodeError:
                if expected_status != 200:
                    print("✅ Non-JSON response expected")
                    return True
                print(f"❌ Response is not valid JSON: {response.text[:200]}...")
                return False
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Run the API endpoint tests."""
    print("=== RAG-LLM Framework API Endpoint Tests ===")
    
    if not check_api_running():
        print("\nPlease start the API server and try again.")
        print("You can start the API server using:")
        print("  python -m uvicorn src.backend.main:app --reload --host 0.0.0.0 --port 8000")
        sys.exit(1)
    
    # Define endpoints to test
    endpoints = [
        {
            "method": "GET",
            "endpoint": "/health",
            "description": "Health check endpoint"
        },
        {
            "method": "GET",
            "endpoint": "/repos",
            "description": "List configured GitHub repositories"
        },
        {
            "method": "POST",
            "endpoint": "/repos/ingest-repos",
            "data": {},
            "description": "Ingest all configured repositories",
            "timeout": 10
        },
        {
            "method": "POST",
            "endpoint": "/query",
            "data": {"query": "What is RAG?"},
            "description": "Query the RAG system"
        },
        {
            "method": "POST",
            "endpoint": "/feedback",
            "data": {"query_id": "test-query-id", "feedback": "This is a test feedback", "rating": 5},
            "description": "Submit feedback for a query"
        },
        {
            "method": "POST",
            "endpoint": "/ingest",
            "data": {
                "source_type": "text",
                "source_data": "This is a test document for ingestion",
                "metadata": {"source": "test"}
            },
            "description": "Ingest text data"
        },
        {
            "method": "GET",
            "endpoint": "/ingested-data",
            "description": "List ingested data"
        },
        {
            "method": "POST",
            "endpoint": "/chat/send",
            "data": {"message": "Hello, how are you?", "conversation_id": "test-conversation"},
            "description": "Send a chat message"
        },
        {
            "method": "GET",
            "endpoint": "/chat/history/test-conversation",
            "description": "Get chat history for a conversation"
        },
        {
            "method": "POST",
            "endpoint": "/chat/feedback",
            "data": {
                "conversation_id": "test-conversation",
                "message_idx": 0,
                "feedback": "This is a test feedback",
                "rating": 5
            },
            "description": "Submit feedback for a chat message"
        },
        {
            "method": "POST",
            "endpoint": "/query-comparison",
            "data": {"query": "What is RAG?", "models": ["llama2", "mistral"]},
            "description": "Compare query results across different models"
        }
    ]
    
    # Test each endpoint
    results = {
        "passed": [],
        "failed": []
    }
    
    for endpoint_info in endpoints:
        method = endpoint_info["method"]
        endpoint = endpoint_info["endpoint"]
        data = endpoint_info.get("data")
        description = endpoint_info.get("description", "")
        timeout = endpoint_info.get("timeout", 5)
        expected_status = endpoint_info.get("expected_status", 200)
        
        if test_endpoint(method, endpoint, data, expected_status, timeout, description):
            results["passed"].append(f"{method} {endpoint}")
        else:
            results["failed"].append(f"{method} {endpoint}")
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"Total endpoints tested: {len(endpoints)}")
    print(f"Passed: {len(results['passed'])}")
    print(f"Failed: {len(results['failed'])}")
    
    if results["failed"]:
        print("\nFailed endpoints:")
        for endpoint in results["failed"]:
            print(f"  - {endpoint}")
        sys.exit(1)
    else:
        print("\nAll endpoint tests passed!")

if __name__ == "__main__":
    main()
