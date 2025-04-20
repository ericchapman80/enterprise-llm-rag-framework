# Installation Guide

This guide provides detailed instructions for setting up the RAG-Enabled LLM Framework.

## Prerequisites

- Rancher Desktop (for local development)
- Kubernetes cluster (for production deployment)
- Helm (for Kubernetes deployment)
- Python 3.10+
- Node.js 16+
- Slack workspace with admin privileges (for Slack integration)
- Backstage instance (for Backstage integration)

## Local Development Setup with Kubernetes

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/rag-llm-framework.git
cd rag-llm-framework
```

### 2. Setting Up Secrets (Optional)

For local development, you can use a `.env` file to manage your secrets:

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file to add your secrets:
   ```bash
   # GitHub Integration
   GITHUB_TOKEN=your_github_token_here
   
   # Slack Bot Integration
   SLACK_BOT_TOKEN=xoxb-your-bot-token-here
   SLACK_APP_TOKEN=xapp-your-app-token-here
   SLACK_SIGNING_SECRET=your-signing-secret-here
   ```

### 3. Using the Makefile

The easiest way to get started is to use the provided Makefile:

```bash
# Complete setup (all steps)
make setup

# Or run individual steps
make check-dependencies
make create-namespace
make build
make load-secrets
make deploy
make configure-hosts
make pull-model
```

To specify a different Kubernetes context or namespace:

```bash
make setup KUBE_CONTEXT=your-context NAMESPACE=your-namespace
```

The Makefile provides the following targets:

| Target | Description |
|--------|-------------|
| `setup` | Complete setup (all steps) |
| `check-dependencies` | Check for required dependencies |
| `create-namespace` | Create Kubernetes namespace |
| `build` | Build Docker images |
| `load-secrets` | Load secrets from .env file |
| `deploy` | Deploy using Helm |
| `configure-hosts` | Configure hosts file |
| `pull-model` | Pull Ollama model |
| `logs` | View logs from backend pod |
| `status` | Check status of deployed pods |
| `clean` | Remove deployed resources |

### 4. Manual Setup

If you prefer to set up manually:

#### a. Install Dependencies

Ensure you have the following installed:
- kubectl
- helm
- docker

#### b. Build Docker Images

```bash
docker build -t rag-llm-backend:latest .
docker build -t rag-llm-slackbot:latest -f Dockerfile.slack .
```

#### c. Deploy with Helm

```bash
# Create namespace
kubectl create namespace rag-llm

# Deploy using Helm
helm upgrade --install rag-llm-framework ./helm/rag-llm-framework \
  --namespace rag-llm \
  --set global.environment=development
```

The API will be available at http://rag-llm.local (you may need to add this to your /etc/hosts file).

## Alternative Local Setup (Without Kubernetes)

### 1. Install Ollama

Follow the [official Ollama installation instructions](https://github.com/ollama/ollama) for your platform.

Once installed, pull the LLM model:

```bash
ollama pull llama2
```

You can replace `llama2` with any other model supported by Ollama.

### 2. Install Backend Dependencies

```bash
cd src/backend
pip install -r requirements.txt
```

### 3. Start the Backend

```bash
cd src/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000.

## Enterprise EKS Deployment

### 1. Build and Push Docker Images

```bash
# Set your ECR repository
ECR_REPO=your-aws-account-id.dkr.ecr.your-region.amazonaws.com

# Login to ECR
aws ecr get-login-password --region your-region | docker login --username AWS --password-stdin $ECR_REPO

# Build and push images
docker build -t $ECR_REPO/rag-llm-backend:latest .
docker push $ECR_REPO/rag-llm-backend:latest

docker build -t $ECR_REPO/rag-llm-slackbot:latest -f Dockerfile.slack .
docker push $ECR_REPO/rag-llm-slackbot:latest
```

### 2. Configure Helm Values for EKS

Create a custom values file for your EKS environment:

```bash
cp helm/rag-llm-framework/values.yaml helm/rag-llm-framework/values-eks.yaml
```

Edit `values-eks.yaml` to update:
- Image repositories to point to your ECR
- Storage classes to use EBS
- Ingress configuration for your domain
- Resource requirements

Example:

```yaml
global:
  environment: production
  imageRegistry: your-aws-account-id.dkr.ecr.your-region.amazonaws.com/

persistence:
  storageClass: gp2

backend:
  ingress:
    enabled: true
    annotations:
      kubernetes.io/ingress.class: alb
      alb.ingress.kubernetes.io/scheme: internet-facing
      alb.ingress.kubernetes.io/target-type: ip
    hosts:
      - host: rag-llm.your-domain.com
        paths:
          - path: /
            pathType: Prefix
```

### 3. Create Kubernetes Secrets

You can create secrets manually:

```bash
kubectl create namespace rag-llm

kubectl create secret generic rag-llm-secrets \
  --namespace rag-llm \
  --from-literal=github-token=your_github_token \
  --from-literal=slack-bot-token=xoxb-your-bot-token \
  --from-literal=slack-app-token=xapp-your-app-token \
  --from-literal=slack-signing-secret=your-signing-secret
```

Or use a `.env` file for easier management:

1. Create a `.env` file with your secrets:
   ```bash
   cp .env.example .env
   # Edit the .env file with your production secrets
   ```

2. Use the provided script to load secrets from the `.env` file:
   ```bash
   chmod +x scripts/load-env-to-k8s.sh
   ./scripts/load-env-to-k8s.sh --namespace rag-llm --env-file .env
   ```

This approach makes it easier to manage secrets across environments and keeps sensitive information out of your command history.

### 4. Deploy to EKS with Helm

```bash
helm upgrade --install rag-llm-framework ./helm/rag-llm-framework \
  --namespace rag-llm \
  --values helm/rag-llm-framework/values-eks.yaml \
  --set secrets.existingSecret=rag-llm-secrets
```

### 5. Verify Deployment

```bash
kubectl get pods -n rag-llm
kubectl get services -n rag-llm
kubectl get ingress -n rag-llm
```

## Helm Chart Configuration

The Helm chart can be configured through the `values.yaml` file. Here are the key configuration sections:

### Global Settings

```yaml
global:
  environment: development  # or production
  imageRegistry: ""  # Set to your registry URL with trailing slash
```

### Backend Configuration

```yaml
backend:
  image:
    repository: rag-llm-backend
    tag: latest
  resources:
    limits:
      cpu: 1000m
      memory: 2Gi
  config:
    llm:
      ollama:
        model_name: llama2  # Change to use a different model
```

### Slack Bot Configuration

```yaml
slackBot:
  image:
    repository: rag-llm-slackbot
    tag: latest
  resources:
    limits:
      cpu: 500m
      memory: 1Gi
```

### Ollama Configuration

```yaml
ollama:
  image:
    repository: ollama/ollama
    tag: latest
  resources:
    limits:
      cpu: 2000m
      memory: 4Gi
```

### Secrets Configuration

```yaml
secrets:
  create: false  # Set to true to create secrets from values
  existingSecret: "rag-llm-secrets"  # Name of existing secret
  values:  # Only used if create is true
    GITHUB_TOKEN: ""
    SLACK_BOT_TOKEN: ""
    SLACK_APP_TOKEN: ""
    SLACK_SIGNING_SECRET: ""
```

## Slack Bot Integration

### 1. Create a Slack App

1. Go to [Slack API](https://api.slack.com/apps) and create a new app
2. Add the following OAuth scopes:
   - `app_mentions:read`
   - `chat:write`
   - `im:history`
   - `im:read`
   - `im:write`
3. Enable Socket Mode
4. Install the app to your workspace
5. Copy the Bot Token (`xoxb-...`) and App Token (`xapp-...`)

### 2. Configure the Slack Bot

Update your Kubernetes secrets with the Slack tokens:

```bash
kubectl create secret generic rag-llm-secrets \
  --namespace rag-llm \
  --from-literal=slack-bot-token=xoxb-your-bot-token \
  --from-literal=slack-app-token=xapp-your-app-token \
  --from-literal=slack-signing-secret=your-signing-secret
```

Or update the `values.yaml` file if using `secrets.create: true`:

```yaml
secrets:
  create: true
  values:
    SLACK_BOT_TOKEN: "xoxb-your-bot-token"
    SLACK_APP_TOKEN: "xapp-your-app-token"
    SLACK_SIGNING_SECRET: "your-signing-secret"
```

## Backstage Integration

### 1. Install the Plugin in Your Backstage App

```bash
cd your-backstage-app
yarn add --cwd packages/app @internal/plugin-rag-llm
```

### 2. Register the Plugin

Edit your `packages/app/src/App.tsx` file to include the plugin:

```tsx
import { RagLlmPage } from '@internal/plugin-rag-llm';

// Add to the routes
<Route path="/rag-llm" element={<RagLlmPage />} />
```

### 3. Add to Sidebar

Edit your `packages/app/src/components/Root/Root.tsx` file:

```tsx
import ChatIcon from '@material-ui/icons/Chat';

// Add to the sidebar items
<SidebarItem icon={ChatIcon} to="rag-llm" text="AI Assistant" />
```

### 4. Configure the Plugin

Create a `app-config.local.yaml` file in your Backstage root:

```yaml
ragLlm:
  apiUrl: http://rag-llm.your-domain.com  # URL to your RAG LLM backend
```

## Changing the LLM Model

To change the LLM model:

1. Update the Helm values file:
   ```yaml
   backend:
     config:
       llm:
         ollama:
           model_name: new-model-name
   ```

2. Upgrade the Helm deployment:
   ```bash
   helm upgrade rag-llm-framework ./helm/rag-llm-framework \
     --namespace rag-llm \
     --values your-values-file.yaml
   ```

3. The Ollama pod will automatically pull the new model on startup.

## Configuring RAG Data Sources

### GitHub Repositories

To add GitHub repositories as data sources:

1. Ensure you have a valid GitHub token with repo access in your secrets
2. Update the ConfigMap in your Helm values:
   ```yaml
   backend:
     config:
       data_sources:
         github:
           repositories:
             - url: https://github.com/your-org/your-repo
               branch: main
               file_extensions: [".md", ".py", ".js"]
   ```

### API Endpoints for Data Ingestion

The backend provides several API endpoints for data ingestion:

1. Text ingestion:
   ```bash
   curl -X POST http://rag-llm.your-domain.com/ingest/text \
     -H "Content-Type: application/json" \
     -d '{"text": "Your free-form text here", "metadata": {"source": "manual", "category": "documentation"}}'
   ```

2. File upload:
   ```bash
   curl -X POST http://rag-llm.your-domain.com/ingest/file \
     -F "file=@/path/to/your/file.md" \
     -F "metadata={\"source\":\"manual\",\"category\":\"documentation\"}"
   ```

3. GitHub repository:
   ```bash
   curl -X POST http://rag-llm.your-domain.com/ingest/github \
     -H "Content-Type: application/json" \
     -d '{"repo_url": "https://github.com/your-org/your-repo", "branch": "main", "file_extensions": [".md", ".py"]}'
   ```

## User Feedback Collection

User feedback is automatically collected through the Slack bot and Backstage plugin interfaces. The feedback is stored and can be used to improve the system over time.

To view collected feedback, access the admin dashboard at `/admin/feedback` (requires admin authentication).
