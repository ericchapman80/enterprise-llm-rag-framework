# RAG-Enabled LLM Framework

A comprehensive framework for deploying a company-specific LLM with Retrieval Augmented Generation (RAG) capabilities, integrated with Slack and Backstage.

## Overview

This framework provides a self-hosted solution for deploying an LLM with RAG capabilities, allowing you to reference:
- GitHub source code repositories (examples of what good looks like)
- Markdown files
- Free-form text
- Interactive chat capabilities

The solution is built on:
- Ollama for LLM hosting
- LangChain for orchestration
- Kubernetes for deployment
- Slack for chat interface
- Backstage for developer portal integration

## Architecture

```mermaid
graph LR
    %% Main components with clear layout
    A[Ollama Service] -->|LLM API| B[RAG Backend]
    B -->|Vector Store| C[(Vector Database)]
    
    %% Data sources
    subgraph "Data Sources"
        F1[GitHub Repos]
        F2[Markdown Files]
        F3[Free-form Text]
    end
    
    F1 -->|Ingestion| B
    F2 -->|Ingestion| B
    F3 -->|Ingestion| B
    
    %% Configuration
    subgraph "Configuration"
        G[Secrets]
        H[ConfigMap]
    end
    
    G -->|Auth| B
    G -->|Auth| E
    H -->|Config| B
    H -->|Config| E
    H -->|Config| A
    
    %% Integration points
    subgraph "Integration Points"
        D[Ingress]
        E[Slack Bot]
        M[Web UI]
    end
    
    B -->|API| D
    E -->|Query/Response| B
    M -->|API| B
    
    %% External services with clear connections
    subgraph "External Services"
        I[Slack Workspace]
        J[Backstage Instance]
        K[GitHub]
    end
    
    I <-->|Events/Messages| E
    J <-->|Plugin API| D
    K <-->|API| B
    
    %% User interactions
    L[User] -->|Chat| I
    L -->|Portal| J
    L -->|Direct API| D
    L -->|Web Browser| M
    
    %% Styling for better visibility
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#bfb,stroke:#333,stroke-width:2px
    style E fill:#fbf,stroke:#333,stroke-width:2px
    style M fill:#ffb,stroke:#333,stroke-width:2px
```

For a more detailed architecture explanation, see the [Architecture Documentation](docs/architecture.md).

## Quick Start

For a quick local setup using any Kubernetes environment (including Rancher Desktop):

```bash
# Clone the repository
git clone https://github.com/your-org/rag-llm-framework.git
cd rag-llm-framework

# Set up environment file
cp .env.example .env
# Edit .env with your configuration

# Run the setup using Make
make setup
```

This will:
1. Check for required dependencies
2. Create a Kubernetes namespace
3. Build Docker images
4. Load secrets from your .env file
5. Deploy the application using Helm charts
6. Configure local access to the application

You can also run individual steps:

```bash
# Build Docker images only
make build

# Deploy to Kubernetes only
make deploy

# Load secrets from .env file
make load-secrets

# Check deployment status
make status

# View logs
make logs
```

## Project Structure

```
rag-llm-framework/
├── Brewfile                # Homebrew dependencies for local setup
├── Dockerfile              # Backend service container
├── Dockerfile.minimal      # Minimal backend container for testing
├── Dockerfile.ollama       # Ollama service container
├── Dockerfile.slack        # Slack bot container
├── Dockerfile.model-controller # Model controller container
├── Makefile                # Make commands for easy deployment and management
├── docker-compose.yml      # Docker Compose configuration for local development
├── helm/                   # Helm charts for Kubernetes deployment
│   └── rag-llm-framework/  # Main Helm chart
│       ├── templates/      # Kubernetes resource templates
│       ├── Chart.yaml      # Chart metadata
│       └── values.yaml     # Default configuration values
├── scripts/                # Utility scripts (see Scripts section below)
├── config/                 # Configuration files
│   └── config.yaml         # Main configuration file
├── docs/                   # Documentation
│   ├── api-endpoints.md    # API endpoints documentation
│   ├── architecture.md     # Architecture documentation
│   ├── github-ingestion-guide.md # GitHub ingestion guide
│   ├── memory-requirements.md # Memory requirements documentation
│   └── ... (more docs)
├── examples/               # Example usage and demos
└── src/
    ├── backend/            # Core backend implementation
    │   ├── main.py         # Main FastAPI application
    │   ├── rag_engine.py   # RAG engine implementation
    │   ├── data_ingestion.py # Data ingestion functionality
    │   ├── model_storage.py # Model storage functionality
    │   └── requirements.txt # Backend dependencies
    └── integrations/
        ├── backstage/      # Backstage integration
        └── slack/          # Slack bot integration
```

## Configuring the RAG Framework

### Changing the LLM Model

The framework uses Ollama to serve LLM models. You can change the model by modifying the Helm chart values:

```yaml
# In helm/rag-llm-framework/values.yaml
backend:
  config:
    llm:
      ollama:
        model_name: llama2  # Change to any model supported by Ollama
```

Available models include:
- `llama2` - Meta's Llama 2 model (default)
- `mistral` - Mistral AI's model
- `gemma` - Google's Gemma model
- `phi` - Microsoft's Phi model
- `codellama` - Specialized for code generation

To use a custom model:

1. Add the model to Ollama:
   ```bash
   kubectl exec -it $(kubectl get pod -l app=ollama -n rag-llm -o jsonpath="{.items[0].metadata.name}") -n rag-llm -- ollama pull your-model-name
   ```

2. Update the Helm values:
   ```bash
   helm upgrade rag-llm-framework ./helm/rag-llm-framework \
     --namespace rag-llm \
     --set backend.config.llm.ollama.model_name=your-model-name
   ```

### Configuring RAG Inputs

The framework supports multiple data sources for RAG:

#### GitHub Repositories

To add GitHub repositories as knowledge sources:

```bash
# Using the API
curl -X POST http://rag-llm.local/ingest/github \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/your-org/your-repo",
    "branch": "main",
    "file_extensions": [".py", ".md", ".js"]
  }'
```

The GitHub token is read from the environment variables or secrets. Make sure to set the `GITHUB_TOKEN` environment variable in your `.env` file:

```
GITHUB_TOKEN=your_github_token_here
```

You can also configure repositories in the Helm values:

```yaml
# In helm/rag-llm-framework/values.yaml
backend:
  config:
    data_sources:
      github:
        repositories:
          - url: "https://github.com/your-org/your-repo"
            branch: "main"
            file_extensions: [".py", ".md", ".js"]
```

For detailed instructions on GitHub repository ingestion, see the [GitHub Ingestion Guide](docs/github-ingestion-guide.md).

For testing the application locally with Ollama, see the [Ollama Local Testing Guide](docs/ollama-local-testing.md).


#### Markdown Files

To add markdown files:

```bash
# Using the API
curl -X POST http://rag-llm.local/ingest/files \
  -F "files=@/path/to/your/file.md" \
  -F "metadata={\"source\": \"documentation\", \"category\": \"user-guide\"}"
```

#### Free-form Text

To add free-form text:

```bash
# Using the API
curl -X POST http://rag-llm.local/ingest/text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your free-form text content here...",
    "metadata": {
      "source": "internal-documentation",
      "category": "best-practices"
    }
  }'
```

### Vector Database Configuration

The framework uses Chroma as the vector database. Configure it in the Helm values:

```yaml
# In helm/rag-llm-framework/values.yaml
backend:
  config:
    embeddings:
      model_name: all-MiniLM-L6-v2  # Embedding model
      vector_db_path: /data/chroma_db  # Storage location
```

### Model Storage Configuration

The framework supports multiple storage options for LLM models to optimize container startup times and resource utilization:

1. **Local Storage** (default): Models are downloaded and stored locally in the container
2. **Cloud Storage**: Models are stored in cloud storage (S3, GCS, Azure Blob Storage)
3. **Network File System (NFS)**: Models are stored on a shared NFS volume

#### Benefits of Cloud Storage

Using cloud storage for LLM models provides several advantages:

- **Faster container startup**: Containers don't need to download the entire model
- **Reduced disk usage**: Only one copy of the model is needed
- **Efficient scaling**: New pods can start quickly without downloading models
- **Centralized management**: Models can be updated in one place

#### Configuring Model Storage

Configure model storage using environment variables:

```bash
# Model Storage Configuration
OLLAMA_STORAGE_TYPE=local  # Options: local, cloud
OLLAMA_CLOUD_PROVIDER=s3   # Options: s3, gcs, azure, nfs
```

Or in the Helm values:

```yaml
# In helm/rag-llm-framework/values.yaml
ollama:
  persistence:
    storage:
      type: local  # Options: local, cloud
      cloud:
        provider: s3  # Options: s3, gcs, azure, nfs
```

For detailed configuration instructions, see the [Model Storage Documentation](docs/model-storage.md).

## Slack Bot Integration

The framework includes a Slack bot for interactive chat capabilities:

### Setting Up the Slack Bot

1. Create a Slack App in the [Slack API Console](https://api.slack.com/apps)
2. Enable Socket Mode and Event Subscriptions
3. Add the following Bot Token Scopes:
   - `chat:write`
   - `app_mentions:read`
   - `channels:history`
   - `im:history`
   - `im:write`
4. Install the app to your workspace
5. Copy the Bot Token, App Token, and Signing Secret

### Configuring the Slack Bot

Update your Helm values with the Slack credentials:

```yaml
# In helm/rag-llm-framework/values.yaml
secrets:
  create: true
  values:
    SLACK_BOT_TOKEN: "xoxb-your-bot-token"
    SLACK_APP_TOKEN: "xapp-your-app-token"
    SLACK_SIGNING_SECRET: "your-signing-secret"
```

Or create a Kubernetes secret manually:

```bash
kubectl create secret generic rag-llm-secrets \
  --namespace rag-llm \
  --from-literal=SLACK_BOT_TOKEN=xoxb-your-bot-token \
  --from-literal=SLACK_APP_TOKEN=xapp-your-app-token \
  --from-literal=SLACK_SIGNING_SECRET=your-signing-secret
```

Then update your Helm values to use the existing secret:

```yaml
# In helm/rag-llm-framework/values.yaml
secrets:
  create: false
  existingSecret: "rag-llm-secrets"
```

For detailed Slack integration instructions, see the [Slack Integration Guide](docs/slack-integration.md).

## Backstage Integration

The framework includes a Backstage plugin for integrating the RAG-enabled LLM into your developer portal:

### Installing the Backstage Plugin

1. Copy the plugin to your Backstage app:
   ```bash
   cp -r src/integrations/backstage/backstage-plugin your-backstage-app/plugins/rag-llm
   ```

2. Add the plugin to your Backstage app's `package.json`:
   ```json
   "dependencies": {
     "@internal/plugin-rag-llm": "link:../plugins/rag-llm"
   }
   ```

3. Register the plugin in your `packages/app/src/App.tsx`:
   ```tsx
   import { RagLlmPage } from '@internal/plugin-rag-llm';
   
   // Add to the routes
   <Route path="/rag-llm" element={<RagLlmPage />} />
   ```

4. Add to the sidebar in `packages/app/src/components/Root/Root.tsx`:
   ```tsx
   import ChatIcon from '@material-ui/icons/Chat';
   
   // Add to the sidebar items
   <SidebarItem icon={ChatIcon} to="rag-llm" text="AI Assistant" />
   ```

5. Configure the plugin in your `app-config.yaml`:
   ```yaml
   ragLlm:
     apiUrl: http://your-rag-llm-backend-url:8000
   ```

For detailed Backstage integration instructions, see the [Backstage Integration Guide](docs/backstage-integration.md).

## Local Development Options

### Option 1: Native Development (No Containers)

For running directly on your machine without any containers:

```bash
# Clone the repository
git clone https://github.com/your-org/rag-llm-framework.git
cd rag-llm-framework

# Make the scripts executable
chmod +x scripts/run-local-native.sh scripts/run-slackbot-native.sh

# Run the backend
./scripts/run-local-native.sh

# In another terminal, run the Slack bot (optional)
./scripts/run-slackbot-native.sh
```

This will:
1. Create a Python virtual environment
2. Install all required dependencies
3. Start Ollama and pull the llama2 model
4. Run the backend and Slack bot directly on your machine

For detailed instructions, see the [Native Setup Guide](docs/local-native-setup.md) or the [Ollama Local Testing Guide](docs/ollama-local-testing.md) for testing specifically with Ollama.

### Option 2: Local Development with Docker Compose

For a containerized setup without requiring Kubernetes:

```bash
# Clone the repository
git clone https://github.com/your-org/rag-llm-framework.git
cd rag-llm-framework

# Run the local setup script
chmod +x scripts/setup-local-dev.sh
./scripts/setup-local-dev.sh
```

This will:
1. Check if Ollama is installed and install it if needed
2. Start the Ollama service and pull the llama2 model
3. Build and start all services using Docker Compose
4. Configure environment variables

For detailed instructions, see the [Local Setup Guide](docs/local-setup.md).

### Option 3: Local Development with Rancher Desktop

Rancher Desktop provides a local Kubernetes environment that closely mirrors your enterprise EKS cluster:

```bash
# Install dependencies
brew bundle

# Start Rancher Desktop
rdctl start

# Deploy using Helm
helm upgrade --install rag-llm-framework ./helm/rag-llm-framework \
  --namespace rag-llm \
  --create-namespace \
  --set global.environment=development
```

To access the application locally:
```bash
# Add local hostname to /etc/hosts
echo "127.0.0.1 rag-llm.local" | sudo tee -a /etc/hosts

# Access the application at http://rag-llm.local
```

## Production Deployment to EKS

For production deployment to your enterprise EKS cluster:

1. Configure AWS credentials:
   ```bash
   aws configure
   ```

2. Update kubeconfig to point to your EKS cluster:
   ```bash
   aws eks update-kubeconfig --name your-eks-cluster-name --region your-aws-region
   ```

3. Build and push Docker images to your container registry:
   ```bash
   # Set your container registry
   export REGISTRY=your-registry.dkr.ecr.region.amazonaws.com
   
   # Build and push images
   docker build -t $REGISTRY/rag-llm-backend:latest .
   docker build -t $REGISTRY/rag-llm-slackbot:latest -f Dockerfile.slack .
   
   docker push $REGISTRY/rag-llm-backend:latest
   docker push $REGISTRY/rag-llm-slackbot:latest
   ```

4. Deploy using Helm:
   ```bash
   helm upgrade --install rag-llm-framework ./helm/rag-llm-framework \
     --namespace rag-llm \
     --create-namespace \
     --set global.environment=production \
     --set global.imageRegistry=$REGISTRY/ \
     --set backend.image.tag=latest \
     --set slackBot.image.tag=latest \
     --set backend.ingress.hosts[0].host=rag-llm.your-domain.com
   ```

For detailed deployment instructions, see the [Installation Guide](docs/installation.md).

## Interactive Chat Interface

The framework includes a standalone web-based chat interface for interacting with the RAG-enabled LLM:

### Web UI

The web UI provides a user-friendly interface for chatting with the LLM:

- **Conversation History**: Maintains context across multiple messages
- **Source Citations**: Shows the sources used to generate responses
- **Feedback Collection**: Allows users to rate responses as helpful or not helpful

To access the web UI:

```bash
# Start the backend server
make run-backend

# Access the web UI at http://localhost:8080
```

### Chat API Endpoints

The framework provides the following chat-specific API endpoints:

#### Send a Message

```bash
curl -X POST http://localhost:8000/chat/send \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What does the repository contain?",
    "conversation_id": "optional-existing-conversation-id"
  }'
```

Response:
```json
{
  "conversation_id": "unique-conversation-id",
  "response": "The repository contains...",
  "sources": [
    {
      "content": "Source content...",
      "metadata": {
        "source": "repository-name",
        "file": "file-path"
      }
    }
  ]
}
```

#### Get Conversation History

```bash
curl -X GET http://localhost:8000/chat/history/your-conversation-id
```

Response:
```json
{
  "conversation_id": "your-conversation-id",
  "messages": [
    {
      "role": "user",
      "content": "What does the repository contain?",
      "timestamp": "2025-04-15T12:30:45Z"
    },
    {
      "role": "assistant",
      "content": "The repository contains...",
      "timestamp": "2025-04-15T12:30:50Z"
    }
  ]
}
```

#### Submit Feedback

```bash
curl -X POST http://localhost:8000/chat/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "your-conversation-id",
    "message_idx": 1,
    "feedback": "helpful",
    "details": "This response was very informative."
  }'
```

Response:
```json
{
  "status": "success",
  "message": "Feedback submitted successfully"
}
```

## User Feedback Collection

The framework includes mechanisms for collecting user feedback to iteratively improve the system:

- **Slack Bot**: Users can provide feedback using reaction emojis or explicit feedback commands
- **Backstage Plugin**: Includes thumbs up/down buttons for each response
- **Web UI**: Provides feedback buttons for each response
- **API Endpoint**: Direct feedback submission via `/chat/feedback` endpoint

Feedback data is stored and can be used to fine-tune the model or improve the RAG system.

## Scripts

The `scripts/` directory contains various utility scripts to help with setup, deployment, and testing:

### Setup Scripts

- **setup-local.sh** - Sets up the framework for local development using Docker Compose
- **setup-local-dev.sh** - Sets up a development environment with all dependencies
- **install-ollama.sh** - Installs Ollama locally for native development
- **make-scripts-executable.sh** - Makes all scripts executable (useful after cloning)

### Deployment Scripts

- **load-env-to-k8s.sh** - Loads environment variables from .env file to Kubernetes secrets
- **fix-kubernetes-deployment.sh** - Fixes common Kubernetes deployment issues
- **fix-k8s-import-error.sh** - Fixes Python import path issues in Kubernetes
- **fix-memory-issue.sh** - Fixes memory allocation issues for Ollama
- **fix-memory-issue-macos.sh** - macOS-specific memory allocation fixes

### Testing Scripts

- **test-api-endpoints.py** - Tests all API endpoints
- **test-github-ingestion.py** - Tests GitHub repository ingestion
- **verify-model.sh** - Verifies that the LLM model is loaded correctly
- **test-certificate.sh** - Tests SSL certificate configuration

### Running Scripts

- **run-local-native.sh** - Runs the backend natively without containers
- **run-local-native-small-model.sh** - Runs with a smaller model for limited resources
- **run-slackbot-native.sh** - Runs the Slack bot natively
- **start-api-server.sh** - Starts just the API server for testing

For detailed usage of each script, see the comments at the top of the script files.

## Testing the Framework

### Testing the API Endpoints

To test the API endpoints:

```bash
# Start the API server
./scripts/start-api-server.sh

# In another terminal, run the test script
python ./scripts/test-api-endpoints.py
```

### Testing GitHub Repository Ingestion

To test GitHub repository ingestion:

1. Ensure your GitHub token is set in the `.env` file:
   ```
   GITHUB_TOKEN=your_github_token_here
   ```

2. Start the API server:
   ```bash
   ./scripts/start-api-server.sh
   ```

3. Test ingestion with a sample repository:
   ```bash
   python ./scripts/test-github-ingestion.py
   ```

4. Or use curl directly:
   ```bash
   curl -X POST http://localhost:8000/ingest/github \
     -H "Content-Type: application/json" \
     -d '{
       "repo_url": "https://github.com/your-org/your-repo",
       "branch": "main",
       "file_extensions": [".md"]
     }'
   ```

5. Test a query with the ingested data:
   ```bash
   curl -X POST http://localhost:8000/query \
     -H "Content-Type: application/json" \
     -d '{
       "query": "What does the repository contain?"
     }'
   ```

### Comparing Responses With and Without RAG

To see the difference RAG makes:

```bash
curl -X POST http://localhost:8000/query-comparison \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What does the repository contain?"
  }'
```

This will return both the RAG-enhanced response and the standard LLM response.

## Documentation

- [Installation Guide](docs/installation.md)
- [Slack Integration](docs/slack-integration.md)
- [Backstage Integration](docs/backstage-integration.md)
- [Model Storage Configuration](docs/model-storage.md)
- [API Endpoints Reference](docs/api-endpoints.md)
- [GitHub Repository Ingestion Guide](docs/github-ingestion-guide.md)
- [Memory Requirements](docs/memory-requirements.md)
- [Troubleshooting Guide](docs/troubleshooting.md)
- [Container Troubleshooting Guide](docs/container-troubleshooting.md)
- [Local Native Setup Guide](docs/local-native-setup.md)
- [Local Setup Guide](docs/local-setup.md)
- [Ollama Installation Guide](docs/ollama-installation.md)

## Troubleshooting Common Issues

### Docker CPU and Memory Allocation Error

If you encounter this error when running Docker Compose:
```
Error response from daemon: Range of CPUs is from 0.01 to 2.00, as there are only 2 CPUs available
```

This occurs because the Ollama service in docker-compose.yml is configured to use more CPUs than are available on your machine. To fix:

1. Edit `docker-compose.yml` and reduce the CPU allocation:
```yaml
ollama:
  deploy:
    resources:
      limits:
        memory: 12G  # Default memory allocation
        cpus: '1.5'  # Reduce this to match your available CPUs
```

2. For machines with limited memory, you may need to adjust memory allocation as well:
```yaml
ollama:
  deploy:
    resources:
      limits:
        memory: 4G  # Reduce this for machines with less RAM
        cpus: '1.0'  # Reduce this for machines with fewer CPUs
```

3. The Ollama service includes a healthcheck configuration to ensure it's fully operational before the backend connects to it:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:11434"]
  interval: 15s
  timeout: 15s
  retries: 10
```

### Import Path Errors

If you see `ModuleNotFoundError: No module named 'rag_engine'` in container logs:

1. For Kubernetes deployments, run the fix script:
```bash
chmod +x scripts/fix-kubernetes-deployment.sh
./scripts/fix-kubernetes-deployment.sh
```

2. For Docker Compose, edit the main.py file to use absolute imports:
```python
# Change from
from rag_engine import RAGEngine
# To
from src.backend.rag_engine import RAGEngine
```

See the [Container Troubleshooting Guide](docs/container-troubleshooting.md) for more detailed solutions.

## License

[MIT License](LICENSE)
