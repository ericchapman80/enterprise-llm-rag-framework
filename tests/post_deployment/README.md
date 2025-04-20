# RAG-LLM Framework Post-Deployment Testing Suite

This directory contains a comprehensive post-deployment testing suite for the RAG-LLM Framework API. The suite is designed to verify that all API endpoints are functioning correctly after deployment.

## Features

- **Modular Design**: Tests are organized by endpoint category for better maintainability
- **Parallel Execution**: Tests can be run in parallel using multithreading for faster execution
- **Comprehensive Reports**: Generates detailed HTML and JSON reports of test results
- **GitHub Workflow Integration**: Automated testing via GitHub Actions
- **Deployment Verification**: Verifies that the API is deployed and healthy before running tests

## Directory Structure

```
tests/post_deployment/
├── __init__.py
├── run_tests.py                # Main test runner script
├── verify_deployment.py        # Deployment verification script
├── core/                       # Core API tests
│   ├── __init__.py
│   └── test_core_api.py
├── chat/                       # Chat API tests
│   ├── __init__.py
│   └── test_chat_api.py
├── repo/                       # Repository management API tests
│   ├── __init__.py
│   └── test_repo_api.py
├── utils/                      # Utility modules
│   ├── __init__.py
│   ├── base_test.py
│   ├── config.py
│   └── test_runner.py
└── reports/                    # Report generation
    ├── __init__.py
    └── report_generator.py
```

## Usage

### Running Tests Locally

```bash
# Run all tests
python tests/post_deployment/run_tests.py

# Run specific test modules
python tests/post_deployment/run_tests.py --modules core,chat

# Run tests sequentially
python tests/post_deployment/run_tests.py --sequential

# Specify API URL
python tests/post_deployment/run_tests.py --url http://api.example.com
```

### Deploy and Test Script

```bash
# Deploy locally and run tests
./scripts/deploy-and-test.sh

# Customize deployment and testing
./scripts/deploy-and-test.sh --port 8080 --modules core --sequential
```

### GitHub Workflow

The testing suite can be triggered via GitHub Actions:

1. Go to the "Actions" tab in the GitHub repository
2. Select the "Post-Deployment API Tests" workflow
3. Click "Run workflow"
4. Enter the API URL and other parameters
5. Click "Run workflow" to start the tests

## Configuration

The testing suite can be configured using environment variables or command line arguments:

- `RAG_API_URL`: Base URL for the API (default: http://localhost:8000)
- `GITHUB_TOKEN`: GitHub token for repository tests
- `PARALLEL_TESTS`: Number of threads for parallel testing (default: auto-detect)
- `TEST_TIMEOUT`: Timeout for API requests in seconds (default: 10)
- `REPORT_FORMAT`: Report formats to generate (default: html,json)

## Test Reports

Test reports are generated in the `test-reports` directory by default. The reports include:

- Test summary (total, passed, failed, error)
- Detailed results for each test
- Duration and timestamp information
- Error messages for failed tests

## Adding New Tests

To add new tests:

1. Create a new test class that inherits from `BaseTest`
2. Implement the `execute` method to perform the test
3. Add the test to the appropriate module or create a new module
4. Update the `get_test_modules` function in `run_tests.py` if needed

Example:

```python
from tests.post_deployment.utils.base_test import BaseTest

class MyNewTest(BaseTest):
    """Test description."""
    
    def __init__(self):
        super().__init__(
            name="My New Test",
            description="Description of what this test verifies."
        )
        
    def execute(self):
        # Implement test logic here
        success, response = self.request("GET", "/my-endpoint")
        return success and "expected_field" in response
```

## Continuous Integration

The testing suite is integrated with GitHub Actions for automated testing after deployment. The workflow can be triggered manually or automatically after deployment to specific environments.

To customize the GitHub workflow, edit the `.github/workflows/post-deployment-tests.yml` file.

## Troubleshooting

If tests are failing, check the following:

1. Verify that the API is running and accessible at the specified URL
2. Check that the API endpoints are implemented correctly
3. Ensure that the required environment variables are set
4. Review the test reports for detailed error messages
5. Try running tests sequentially to identify specific failing tests
