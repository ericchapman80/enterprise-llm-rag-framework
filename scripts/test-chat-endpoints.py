"""
Test script for the chat endpoints of the RAG-LLM Framework.
This script tests the following endpoints:
- /chat/send - Send a message to the chat
- /chat/history/{conversation_id} - Get chat history
- /chat/feedback - Submit feedback for a chat message
"""
import requests
import json
import sys
import time
import argparse

def test_send_message(base_url, message="Hello, how can you help me with GitHub repositories?"):
    """Test sending a message to the chat."""
    print(f"\n=== Testing /chat/send endpoint with message: '{message}' ===")
    
    try:
        response = requests.post(
            f"{base_url}/chat/send",
            json={"message": message},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Response received successfully:")
            print(f"Conversation ID: {result.get('conversation_id')}")
            print(f"Response: {result.get('response')[:100]}...")
            if result.get('sources'):
                print(f"Sources: {len(result.get('sources'))} sources found")
            else:
                print("Sources: No sources found")
            return result
        else:
            print(f"Error response: {response.text}")
            return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def test_continue_conversation(base_url, conversation_id, message="Tell me more about that."):
    """Test continuing a conversation with a follow-up message."""
    print(f"\n=== Testing conversation continuation with message: '{message}' ===")
    
    try:
        response = requests.post(
            f"{base_url}/chat/send",
            json={
                "message": message,
                "conversation_id": conversation_id
            },
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Response received successfully:")
            print(f"Conversation ID: {result.get('conversation_id')}")
            print(f"Response: {result.get('response')[:100]}...")
            if result.get('sources'):
                print(f"Sources: {len(result.get('sources'))} sources found")
            else:
                print("Sources: No sources found")
            return result
        else:
            print(f"Error response: {response.text}")
            return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def test_get_history(base_url, conversation_id):
    """Test getting the chat history for a conversation."""
    print(f"\n=== Testing /chat/history/{conversation_id} endpoint ===")
    
    try:
        response = requests.get(
            f"{base_url}/chat/history/{conversation_id}"
        )
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Chat history received successfully:")
            print(f"Conversation ID: {result.get('conversation_id')}")
            print(f"Messages: {len(result.get('messages'))} messages found")
            for i, msg in enumerate(result.get('messages', [])):
                print(f"  Message {i+1}: {msg.get('role')} - {msg.get('content')[:50]}...")
            return result
        else:
            print(f"Error response: {response.text}")
            return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def test_submit_feedback(base_url, conversation_id, message_idx=0, feedback="helpful"):
    """Test submitting feedback for a chat message."""
    print(f"\n=== Testing /chat/feedback endpoint ===")
    
    try:
        response = requests.post(
            f"{base_url}/chat/feedback",
            json={
                "conversation_id": conversation_id,
                "message_idx": message_idx,
                "feedback": feedback,
                "details": "This response was very informative."
            },
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Feedback submitted successfully:")
            print(f"Status: {result.get('status')}")
            print(f"Message: {result.get('message')}")
            return result
        else:
            print(f"Error response: {response.text}")
            return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def check_openapi_docs(base_url):
    """Check if the chat endpoints are documented in the OpenAPI schema."""
    print("\n=== Checking OpenAPI documentation for chat endpoints ===")
    
    try:
        response = requests.get(f"{base_url}/openapi.json")
        
        if response.status_code == 200:
            schema = response.json()
            paths = schema.get("paths", {})
            
            chat_endpoints = [
                "/chat/send",
                "/chat/history/{conversation_id}",
                "/chat/feedback"
            ]
            
            for endpoint in chat_endpoints:
                if endpoint in paths:
                    print(f"✅ Endpoint {endpoint} is documented")
                else:
                    print(f"❌ Endpoint {endpoint} is not documented")
            
            return True
        else:
            print(f"❌ Failed to get OpenAPI schema: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error checking OpenAPI docs: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Test the chat endpoints of the RAG-LLM Framework")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Base URL of the API server")
    args = parser.parse_args()
    
    base_url = args.base_url
    
    print("=== RAG-LLM Framework Chat Endpoints Test ===")
    print(f"Base URL: {base_url}")
    
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code != 200:
            print(f"❌ API is not running or health check failed: {response.status_code}")
            sys.exit(1)
        print("✅ API is running")
    except requests.exceptions.ConnectionError:
        print("❌ API is not running")
        print(f"Please start the API server at {base_url}")
        sys.exit(1)
    
    result = test_send_message(base_url)
    if not result:
        print("❌ Failed to send message")
        sys.exit(1)
    
    conversation_id = result.get("conversation_id")
    
    time.sleep(1)  # Wait a bit to avoid rate limiting
    continue_result = test_continue_conversation(base_url, conversation_id)
    if not continue_result:
        print("❌ Failed to continue conversation")
    
    time.sleep(1)  # Wait a bit to avoid rate limiting
    history_result = test_get_history(base_url, conversation_id)
    if not history_result:
        print("❌ Failed to get chat history")
    
    time.sleep(1)  # Wait a bit to avoid rate limiting
    feedback_result = test_submit_feedback(base_url, conversation_id)
    if not feedback_result:
        print("❌ Failed to submit feedback")
    
    check_openapi_docs(base_url)
    
    print("\n=== Chat Endpoints Test Complete ===")

if __name__ == "__main__":
    main()
