# RAG-LLM Framework Complete Package

This package contains all files needed to run the RAG-LLM Framework in:
- Local development environment
- Docker Compose environment
- Kubernetes environment

## Quick Start

### Prerequisites
- Docker and Docker Compose for container-based deployment
- Kubernetes cluster (or Rancher Desktop) for Kubernetes deployment
- Python 3.10+ for local development
- Zscaler certificate (if in corporate environment)

### Docker Compose Deployment

1. Unzip the package:
   ```
   unzip rag-llm-complete-package.zip
   cd rag-llm-framework
   ```

2. Copy your Zscaler certificate (if needed):
   ```
   # Place your Zscaler certificate in the project root
   cp /path/to/your/zscaler.crt .
   ```

3. Create a .env file from the example:
   ```
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. Build and run with Docker Compose:
   ```
   make build
   make up
   ```

5. Test the certificate installation:
   ```
   chmod +x scripts/test-certificate.sh
   ./scripts/test-certificate.sh
   ```

6. Access the API at http://localhost:8000

### Kubernetes Deployment

1. Ensure your Kubernetes context is set correctly:
   ```
   kubectl config current-context
   ```

2. Deploy to Kubernetes:
   ```
   make deploy
   ```

3. Test the certificate installation:
   ```
   chmod +x scripts/test-k8s-certificate.sh
   ./scripts/test-k8s-certificate.sh
   ```

4. Access the API through the Ingress URL (default: http://rag-llm.local)

### Local Native Development

1. Set up the local environment:
   ```
   make setup-local
   ```

2. Run the backend:
   ```
   make run-local
   ```

3. Run the Slack bot (if configured):
   ```
   make run-slackbot
   ```

## Configuration

### Changing the LLM Model

You can change the LLM model by:

1. Editing the `.env` file:
   ```
   # LLM Configuration
   OLLAMA_MODEL_NAME=llama2  # Change to your preferred model
   ```

2. Or updating the Helm values for Kubernetes:
   ```
   helm upgrade rag-llm-framework ./helm/rag-llm-framework --set backend.config.llm.ollama.model_name=YOUR_MODEL
   ```

### Adding Data Sources

The framework supports multiple data sources:
- Text files
- Markdown files
- GitHub repositories
- Direct text input

Use the API endpoints to ingest data:
- `/ingest/text` - For direct text input
- `/ingest/file` - For file uploads
- `/ingest/github` - For GitHub repositories

## Troubleshooting

### Certificate Issues

If you encounter certificate errors:
```
Error: pull model manifest: Get "https://registry.ollama.ai/v2/library/llama2/manifests/latest": tls: failed to verify certificate
```

Ensure your Zscaler certificate is:
1. Placed in the project root as `zscaler.crt`
2. Properly mounted in the container (check docker-compose.yml)
3. Added to the CA certificates store

### Import Errors

If you see import errors in the backend:
```
ModuleNotFoundError: No module named 'rag_engine'
```

Run the fix script:
```
./scripts/fix-import-error.sh
```

### Resource Constraints

If you encounter resource limit errors:
```
Error response from daemon: Range of CPUs is from 0.01 to 2.00, as there are only 2 CPUs available
```

Adjust the CPU limits in docker-compose.yml:
```
./scripts/fix-resource-limits-updated.sh
```

## Additional Resources

- Full documentation in the `docs/` directory
- Example scripts in the `examples/` directory
- Configuration templates in the `config/` directory

For more detailed information, refer to the main README.md file.
