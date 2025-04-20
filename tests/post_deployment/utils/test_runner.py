"""
Test runner with multithreading support for the RAG-LLM Framework post-deployment tests.
"""
import concurrent.futures
import logging
import time
from typing import List, Dict, Any, Optional
import os
import multiprocessing

from tests.post_deployment.utils.config import PARALLEL_TESTS

logger = logging.getLogger("rag-tests")

class TestRunner:
    """Runs tests in parallel using multithreading."""
    
    def __init__(self, thread_count: Optional[int] = None):
        self.thread_count = thread_count or self._get_optimal_thread_count()
        self.results = {
            "passed": [],
            "failed": [],
            "error": []
        }
        self.start_time = None
        self.end_time = None
        
    def _get_optimal_thread_count(self) -> int:
        """Determine the optimal number of threads for test execution."""
        if PARALLEL_TESTS > 0:
            logger.info(f"Using {PARALLEL_TESTS} threads for testing (from configuration)")
            return PARALLEL_TESTS
            
        cpu_count = multiprocessing.cpu_count()
        default_thread_count = max(2, min(cpu_count, 8))
        logger.info(f"Using {default_thread_count} threads for testing (auto-detected from {cpu_count} CPU cores)")
        return default_thread_count
        
    def run_test(self, test):
        """Run a single test and return the result."""
        result = test.run()
        logger.info(f"Test {result['name']} completed with status: {result['status']}")
        return result
        
    def run_tests(self, tests: List[Any], sequential: bool = False) -> Dict[str, Any]:
        """Run a list of tests, either sequentially or in parallel."""
        self.start_time = time.time()
        
        if sequential:
            logger.info(f"Running {len(tests)} tests sequentially")
            results = [self.run_test(test) for test in tests]
        else:
            logger.info(f"Running {len(tests)} tests in parallel with {self.thread_count} threads")
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.thread_count) as executor:
                results = list(executor.map(self.run_test, tests))
        
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        
        for result in results:
            if result["status"] == "Pass":
                self.results["passed"].append(result)
            elif result["status"] == "Fail":
                self.results["failed"].append(result)
            else:
                self.results["error"].append(result)
        
        summary = {
            "total_tests": len(tests),
            "passed": len(self.results["passed"]),
            "failed": len(self.results["failed"]),
            "error": len(self.results["error"]),
            "duration": duration,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "results": results
        }
        
        logger.info(f"Test run completed in {duration:.2f}s")
        logger.info(f"Total: {summary['total_tests']}, "
                    f"Passed: {summary['passed']}, "
                    f"Failed: {summary['failed']}, "
                    f"Error: {summary['error']}")
        
        return summary
