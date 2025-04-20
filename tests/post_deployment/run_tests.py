"""
Main test script for the RAG-LLM Framework post-deployment tests.
"""
import argparse
import logging
import time
import sys
import os
from typing import List
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from tests.post_deployment.utils.config import REPORT_FORMAT
from tests.post_deployment.utils.test_runner import TestRunner
from tests.post_deployment.reports.report_generator import generate_reports

from tests.post_deployment.core.test_core_api import core_tests
from tests.post_deployment.chat.test_chat_api import get_chat_tests
from tests.post_deployment.repo.test_repo_api import repo_tests

logger = logging.getLogger("rag-tests")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="RAG-LLM Framework Post-Deployment API Tests")
    
    parser.add_argument("--url", help="Base URL for the API (default: from environment or localhost:8000)")
    parser.add_argument("--threads", type=int, help="Number of threads for parallel test execution")
    parser.add_argument("--timeout", type=int, help="Timeout for API requests in seconds")
    parser.add_argument("--report", help="Report format(s) to generate (comma-separated: html,json)")
    parser.add_argument("--output-dir", default="test-reports", help="Directory to store test reports")
    parser.add_argument("--modules", help="Test modules to run (comma-separated: core,chat,repo)")
    parser.add_argument("--sequential", action="store_true", help="Run tests sequentially instead of in parallel")
    
    return parser.parse_args()

def configure_from_args(args):
    """Configure the test environment from command line arguments."""
    if args.url:
        os.environ["RAG_API_URL"] = args.url
        
    if args.threads:
        os.environ["PARALLEL_TESTS"] = str(args.threads)
        
    if args.timeout: 
        os.environ["TEST_TIMEOUT"] = str(args.timeout)
        
    if args.report:
        os.environ["REPORT_FORMAT"] = args.report
        
    if args.output_dir:
        os.makedirs(args.output_dir, exist_ok=True)

def get_test_modules(modules_arg: str = None) -> List:
    """Get test modules based on command line argument."""
    all_modules = ["core", "chat", "repo"]
    
    if not modules_arg:
        modules = all_modules
    else:
        modules = [m.strip() for m in modules_arg.split(",")]
        
    tests = []
    
    if "core" in modules:
        tests.extend(core_tests)
        
    if "chat" in modules:
        tests.extend(get_chat_tests())
        
    if "repo" in modules:
        tests.extend(repo_tests)
        
    return tests

def main():
    """Run the post-deployment tests."""
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"=== RAG-LLM Framework Post-Deployment API Tests ===")
    print(f"Started at: {timestamp}")
    
    args = parse_args()
    configure_from_args(args)
    
    tests = get_test_modules(args.modules)
    
    if not tests:
        logger.error("No test modules selected. Exiting.")
        sys.exit(1)
        
    print(f"Running {len(tests)} tests from selected modules")
    
    runner = TestRunner(args.threads)
    results = runner.run_tests(tests, sequential=args.sequential)
    
    report_formats = [f.strip() for f in REPORT_FORMAT.split(",")]
    reports = generate_reports(results, report_formats)
    
    print("\n=== Test Summary ===")
    print(f"Total tests: {results['total_tests']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print(f"Error: {results['error']}")
    print(f"Duration: {results['duration']:.2f} seconds")
    
    for fmt, path in reports.items():
        print(f"{fmt.upper()} report: {path}")
        
    if results['failed'] > 0 or results['error'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
