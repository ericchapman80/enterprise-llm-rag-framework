"""
Test script for the RAG-LLM Framework API endpoints.
"""
import requests
import json
import sys
import os

BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health check endpoint."""
    print("\n--- Testing /health endpoint ---")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_ingested_data():
    """Test the ingested-data endpoint."""
    print("\n--- Testing /ingested-data endpoint ---")
    try:
        response = requests.get(f"{BASE_URL}/ingested-data")
        print(f"Status code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_flush_database():
    """Test the flush-database endpoint."""
    print("\n--- Testing /flush-database endpoint ---")
    try:
        response = requests.post(f"{BASE_URL}/flush-database")
        print(f"Status code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_query_comparison():
    """Test the query-comparison endpoint."""
    print("\n--- Testing /query-comparison endpoint ---")
    try:
        data = {"query": "What is RAG?"}
        response = requests.post(f"{BASE_URL}/query-comparison", json=data)
        print(f"Status code: {response.status_code}")
        print(f"Response keys: {list(response.json().keys())}")
        print(f"With RAG response: {response.json().get('with_rag', {}).get('response', '')[:100]}...")
        print(f"Without RAG response: {response.json().get('without_rag', {}).get('response', '')[:100]}...")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("=== Testing RAG-LLM Framework API Endpoints ===")
    
    if not test_health():
        print("\nError: API is not running or health check failed.")
        print("Please start the API server using one of the following methods:")
        print("1. Local native: ./scripts/run-local-native.sh")
        print("2. Kubernetes: kubectl port-forward svc/rag-llm-backend -n rag-llm 8000:8000")
        sys.exit(1)
    
    test_ingested_data()
    test_flush_database()
    test_query_comparison()
    
    print("\n=== All tests completed ===")

if __name__ == "__main__":
    main()
