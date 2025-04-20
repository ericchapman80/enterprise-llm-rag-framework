# RAG-LLM Framework Verification Checklist

This document provides a checklist to verify that all components of the RAG-LLM Framework are functioning correctly after deployment.

## Core Functionality Verification

### RAG Backend

- [ ] **Ollama Integration**
  - [ ] Ollama pod is running (`kubectl get pods -n rag-llm`)
  - [ ] Ollama model is successfully pulled (`kubectl exec -it $(kubectl get pod -l app=ollama -n rag-llm -o jsonpath="{.items[0].metadata.name}") -n rag-llm -- ollama list`)
  - [ ] Backend can communicate with Ollama service

- [ ] **LangChain Integration**
  - [ ] Vector database is initialized
  - [ ] Embeddings are generated correctly
  - [ ] RAG retrieval returns relevant context

- [ ] **Data Ingestion**
  - [ ] GitHub repository ingestion works
    ```bash
    curl -X POST http://rag-llm.local/ingest/github \
      -H "Content-Type: application/json" \
      -d '{
        "repo_url": "https://github.com/your-org/your-repo",
        "branch": "main",
        "file_extensions": [".py", ".md", ".js"],
        "github_token": "your-github-token"
      }'
    ```
  - [ ] Markdown file ingestion works
    ```bash
    curl -X POST http://rag-llm.local/ingest/files \
      -F "files=@/path/to/your/file.md" \
      -F "metadata={\"source\": \"documentation\", \"category\": \"user-guide\"}"
    ```
  - [ ] Free-form text ingestion works
    ```bash
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

- [ ] **Query API**
  - [ ] Query endpoint returns relevant responses
    ```bash
    curl -X POST http://rag-llm.local/query \
      -H "Content-Type: application/json" \
      -d '{
        "query": "What are the best practices for code reviews?",
        "conversation_id": null
      }'
    ```
  - [ ] Responses include source references
  - [ ] Conversation history is maintained correctly

### Slack Bot Integration

- [ ] **Bot Deployment**
  - [ ] Slack bot pod is running (`kubectl get pods -n rag-llm`)
  - [ ] Bot connects to Slack successfully

- [ ] **Chat Functionality**
  - [ ] Bot responds to direct messages
  - [ ] Bot responds to mentions in channels
  - [ ] Responses are relevant to queries

- [ ] **Feedback Collection**
  - [ ] Users can provide feedback using reaction emojis
  - [ ] Feedback is stored and accessible

### Backstage Integration

- [ ] **Plugin Installation**
  - [ ] Plugin is installed in Backstage
  - [ ] Plugin appears in the sidebar

- [ ] **Chat Interface**
  - [ ] Chat interface loads correctly
  - [ ] Users can send messages
  - [ ] Responses are displayed correctly

- [ ] **Feedback Collection**
  - [ ] Thumbs up/down buttons work
  - [ ] Feedback is submitted to the backend

## Configuration Verification

### LLM Model Configuration

- [ ] **Changing Models**
  - [ ] Update Helm values to use a different model
    ```bash
    helm upgrade rag-llm-framework ./helm/rag-llm-framework \
      --namespace rag-llm \
      --set backend.config.llm.ollama.model_name=mistral
    ```
  - [ ] Verify the new model is used for responses

### RAG Configuration

- [ ] **Vector Database**
  - [ ] Persistence works across restarts
  - [ ] Embeddings are stored correctly

- [ ] **Retrieval Parameters**
  - [ ] Adjust retrieval parameters in config
    ```yaml
    # In helm/rag-llm-framework/values.yaml
    backend:
      config:
        retrieval:
          chunk_size: 1000
          chunk_overlap: 200
          top_k: 5
    ```
  - [ ] Verify changes affect retrieval results

## Deployment Verification

### Local Deployment with Rancher Desktop

- [ ] **Setup Script**
  - [ ] `setup-rancher.sh` script runs successfully
  - [ ] All components are deployed correctly

- [ ] **Ingress**
  - [ ] Application is accessible at http://rag-llm.local
  - [ ] API endpoints are reachable

### EKS Deployment Preparation

- [ ] **Helm Chart Compatibility**
  - [ ] Helm chart values support EKS-specific configuration
  - [ ] Resource requests and limits are appropriate for EKS

- [ ] **Secrets Management**
  - [ ] Secrets can be managed using Kubernetes secrets
  - [ ] External secret management is supported

## User Feedback Loop

- [ ] **Feedback Collection**
  - [ ] Feedback is collected from all interfaces (Slack, Backstage)
  - [ ] Feedback data is stored persistently

- [ ] **Feedback Analysis**
  - [ ] Feedback can be exported for analysis
  - [ ] System can be improved based on feedback

## Troubleshooting

If you encounter issues during verification, check the following:

1. **Pod Status**
   ```bash
   kubectl get pods -n rag-llm
   ```

2. **Pod Logs**
   ```bash
   kubectl logs -f <pod-name> -n rag-llm
   ```

3. **Service Status**
   ```bash
   kubectl get services -n rag-llm
   ```

4. **Ingress Status**
   ```bash
   kubectl get ingress -n rag-llm
   ```

5. **ConfigMap and Secrets**
   ```bash
   kubectl get configmap -n rag-llm
   kubectl get secrets -n rag-llm
   ```

## Next Steps After Verification

Once all verification steps are complete:

1. Document any issues or improvements needed
2. Plan for production deployment to EKS
3. Set up monitoring and alerting
4. Establish a feedback review process
5. Create a plan for regular model and data updates
