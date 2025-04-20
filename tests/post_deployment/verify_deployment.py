"""
Deployment verification script for the RAG-LLM Framework post-deployment tests.
"""
import argparse
import logging
import sys
import time
import requests
from datetime import datetime

logger = logging.getLogger("rag-deployment")
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="RAG-LLM Framework Deployment Verification")
    
    parser.add_argument("--url", required=True, help="Base URL for the API to verify")
    parser.add_argument("--retries", type=int, default=5, help="Number of retries for health check")
    parser.add_argument("--delay", type=int, default=5, help="Delay between retries in seconds")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout for API requests in seconds")
    
    return parser.parse_args()

def verify_deployment(url, retries=5, delay=5, timeout=10):
    """Verify that the API is deployed and healthy."""
    logger.info(f"Verifying deployment at {url}")
    
    for attempt in range(1, retries + 1):
        try:
            logger.info(f"Attempt {attempt}/{retries} to verify deployment")
            
            response = requests.get(f"{url}/health", timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    logger.info(f"Deployment verified successfully: {data}")
                    return True
                else:
                    logger.warning(f"API responded but status is not healthy: {data}")
            else:
                logger.warning(f"API responded with status code: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Error connecting to API: {str(e)}")
            
        if attempt < retries:
            logger.info(f"Waiting {delay} seconds before next attempt...")
            time.sleep(delay)
            
    logger.error("Failed to verify deployment after all retries")
    return False

def main():
    """Run the deployment verification."""
    start_time = datetime.now()
    
    print(f"=== RAG-LLM Framework Deployment Verification ===")
    print(f"Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    args = parse_args()
    
    success = verify_deployment(
        args.url, 
        retries=args.retries,
        delay=args.delay,
        timeout=args.timeout
    )
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\n=== Verification Summary ===")
    print(f"Status: {'SUCCESS' if success else 'FAILED'}")
    print(f"Duration: {duration:.2f} seconds")
    print(f"URL: {args.url}")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
