"""
Test script to verify the FastAPI OpenAPI documentation.
This script checks if all endpoints are properly documented in the OpenAPI schema.
"""
import requests
import json
import sys
import os
from pprint import pprint

def check_api_running():
    """Check if the API is running."""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ API is running")
            return True
        else:
            print(f"❌ API returned status code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ API is not running")
        return False

def get_openapi_schema():
    """Get the OpenAPI schema from the API."""
    try:
        response = requests.get("http://localhost:8000/openapi.json")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get OpenAPI schema: {response.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        print("❌ API is not running")
        return None

def check_endpoint_documentation(schema, endpoint_path, method="post"):
    """Check if an endpoint is properly documented in the OpenAPI schema."""
    if not schema:
        return False
    
    paths = schema.get("paths", {})
    if endpoint_path not in paths:
        print(f"❌ Endpoint {endpoint_path} not found in OpenAPI schema")
        return False
    
    endpoint_info = paths[endpoint_path].get(method.lower())
    if not endpoint_info:
        print(f"❌ Method {method.upper()} not found for endpoint {endpoint_path}")
        return False
    
    print(f"✅ Endpoint {method.upper()} {endpoint_path} is documented")
    print(f"   Summary: {endpoint_info.get('summary', 'No summary')}")
    print(f"   Description: {endpoint_info.get('description', 'No description')}")
    
    if "requestBody" in endpoint_info:
        print(f"   Request body schema: ✅")
    else:
        print(f"   Request body schema: ❌ Not documented")
    
    if "responses" in endpoint_info and "200" in endpoint_info["responses"]:
        print(f"   Response schema: ✅")
    else:
        print(f"   Response schema: ❌ Not documented")
    
    return True

def test_query_comparison_endpoint():
    """Test the query comparison endpoint."""
    print("\n--- Testing Query Comparison Endpoint ---")
    try:
        response = requests.post(
            "http://localhost:8000/query-comparison",
            json={"query": "What does the repository contain?"},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Response received successfully")
            return True
        else:
            print(f"Error response: {response.text}")
            return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def main():
    """Main function."""
    print("=== Testing FastAPI OpenAPI Documentation ===")
    
    if not check_api_running():
        print("\nPlease start the API server and try again.")
        print("You can start the API server using:")
        print("  ./scripts/start-api-server.sh")
        sys.exit(1)
    
    schema = get_openapi_schema()
    if not schema:
        sys.exit(1)
    
    print("\n--- Checking Endpoint Documentation ---")
    
    endpoints = [
        ("/query", "post"),
        ("/feedback", "post"),
        ("/ingest", "post"),
        ("/ingest/github", "post"),
        ("/ingested", "get"),
        ("/ingested-data", "get"),
        ("/flush-database", "post"),
        ("/query-comparison", "post"),
        ("/health", "get")
    ]
    
    all_documented = True
    for endpoint, method in endpoints:
        if not check_endpoint_documentation(schema, endpoint, method):
            all_documented = False
    
    if all_documented:
        print("\n✅ All endpoints are properly documented in the OpenAPI schema")
    else:
        print("\n❌ Some endpoints are not properly documented in the OpenAPI schema")
    
    test_query_comparison_endpoint()
    
    print("\n=== OpenAPI Documentation Test Complete ===")

if __name__ == "__main__":
    main()
