"""
Test script for GitHub repository ingestion in the RAG-LLM Framework.
This script uses port 8001 instead of the default 8000.
"""
import requests
import json
import sys
import os
import time
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8001"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

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

def test_github_ingestion(repo_url, branch="main", file_extensions=None):
    """Test GitHub repository ingestion."""
    if file_extensions is None:
        file_extensions = [".md"]
    
    print(f"\n--- Testing GitHub Repository Ingestion ---")
    print(f"Repository: {repo_url}")
    print(f"Branch: {branch}")
    print(f"File Extensions: {file_extensions}")
    
    data = {
        "repo_url": repo_url,
        "branch": branch,
        "file_extensions": file_extensions
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/ingest/github",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"Response: {json.dumps(result, indent=2)}")
                return True
            except json.JSONDecodeError:
                print(f"Response is not valid JSON: {response.text}")
                return False
        else:
            print(f"Error response: {response.text}")
            return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_query(query_text):
    """Test a query to verify ingestion."""
    print(f"\n--- Testing Query with Ingested Data ---")
    print(f"Query: {query_text}")
    
    data = {"query": query_text}
    
    try:
        response = requests.post(
            f"{BASE_URL}/query",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"Response: {json.dumps(result, indent=2)}")
                return True
            except json.JSONDecodeError:
                print(f"Response is not valid JSON: {response.text}")
                return False
        else:
            print(f"Error response: {response.text}")
            return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def main():
    """Run the GitHub ingestion test."""
    print("=== GitHub Repository Ingestion Test ===")
    
    if not GITHUB_TOKEN:
        print("\n❌ GitHub token is not set in the .env file")
        print("Please set the GITHUB_TOKEN environment variable and try again.")
        sys.exit(1)
    else:
        print(f"✅ GitHub token is set: {GITHUB_TOKEN[:4]}...{GITHUB_TOKEN[-4:]}")
    
    if not check_api_running():
        print("\nStarting API server on port 8001...")
        print("Please run in another terminal:")
        print("cd /home/ubuntu/rag-llm-framework/src/backend && PYTHONPATH=/home/ubuntu/rag-llm-framework python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001")
        sys.exit(1)
    
    repo_url = "https://github.com/wwg-internal/productcore-launchpoint"
    branch = "main"
    file_extensions = [".md"]
    
    if not test_github_ingestion(repo_url, branch, file_extensions):
        print("\n❌ GitHub repository ingestion failed")
        print("Please check the API logs for more information.")
        sys.exit(1)
    
    print("\nWaiting for ingestion to complete...")
    time.sleep(5)
    
    query_text = "What is the purpose of the productcore-launchpoint repository?"
    if not test_query(query_text):
        print("\n❌ Query test failed")
        print("Please check the API logs for more information.")
        sys.exit(1)
    
    print("\n=== All tests completed successfully ===")

if __name__ == "__main__":
    main()
