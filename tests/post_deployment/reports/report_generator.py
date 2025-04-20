"""
Report generators for the RAG-LLM Framework post-deployment tests.
"""
import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger("rag-tests")

class ReportGenerator:
    """Base class for test report generators."""
    
    def __init__(self, output_dir: str = "test-reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def generate(self, results: Dict[str, Any], test_run_id: str = None) -> str:
        """Generate a report from test results."""
        raise NotImplementedError("Subclasses must implement generate method")


class JsonReportGenerator(ReportGenerator):
    """Generates test reports in JSON format."""
    
    def generate(self, results: Dict[str, Any], test_run_id: str = None) -> str:
        """Generate a JSON report from test results."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_run_id = test_run_id or timestamp
        
        filename = f"{self.output_dir}/test_report_{test_run_id}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
            
        logger.info(f"JSON report generated: {filename}")
        return filename


class HtmlReportGenerator(ReportGenerator):
    """Generates test reports in HTML format."""
    
    def generate(self, results: Dict[str, Any], test_run_id: str = None) -> str:
        """Generate an HTML report from test results."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_run_id = test_run_id or timestamp
        
        filename = f"{self.output_dir}/test_report_{test_run_id}.html"
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>RAG-LLM Framework API Test Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #333; }
                .summary { background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
                .test-table { width: 100%; border-collapse: collapse; }
                .test-table th, .test-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                .test-table th { background-color: #f2f2f2; }
                .pass { background-color: #dff0d8; }
                .fail { background-color: #f2dede; }
                .error { background-color: #fcf8e3; }
                .details { margin-top: 10px; font-size: 0.9em; }
            </style>
        </head>
        <body>
            <h1>RAG-LLM Framework API Test Report</h1>
        """
        
        start_time = datetime.fromtimestamp(results["start_time"]) if "start_time" in results else datetime.now()
        duration = results.get("duration", 0)
        
        html += f"""
            <div class="summary">
                <h2>Summary</h2>
                <p><strong>Date:</strong> {start_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Duration:</strong> {duration:.2f} seconds</p>
                <p><strong>Total Tests:</strong> {results.get('total_tests', 0)}</p>
                <p><strong>Passed:</strong> {results.get('passed', 0)}</p>
                <p><strong>Failed:</strong> {results.get('failed', 0)}</p>
                <p><strong>Error:</strong> {results.get('error', 0)}</p>
            </div>
        """
        
        html += """
            <h2>Test Results</h2>
            <table class="test-table">
                <thead>
                    <tr>
                        <th>Test Name</th>
                        <th>Description</th>
                        <th>Status</th>
                        <th>Duration (s)</th>
                        <th>Error</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for result in results.get("results", []):
            status_class = "pass" if result.get("status") == "Pass" else "fail" if result.get("status") == "Fail" else "error"
            error = result.get("error", "")
            
            html += f"""
                <tr class="{status_class}">
                    <td>{result.get('name', '')}</td>
                    <td>{result.get('description', '')}</td>
                    <td>{result.get('status', '')}</td>
                    <td>{result.get('duration', 0):.2f}</td>
                    <td>{error}</td>
                </tr>
            """
        
        html += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        with open(filename, 'w') as f:
            f.write(html)
            
        logger.info(f"HTML report generated: {filename}")
        return filename


def generate_reports(results: Dict[str, Any], formats: List[str] = ["html", "json"]) -> Dict[str, str]:
    """Generate reports in the specified formats."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    reports = {}
    
    if "json" in formats:
        generator = JsonReportGenerator()
        reports["json"] = generator.generate(results, timestamp)
        
    if "html" in formats:
        generator = HtmlReportGenerator()
        reports["html"] = generator.generate(results, timestamp)
        
    return reports
