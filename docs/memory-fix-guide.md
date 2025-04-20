# Memory Fix Guide for RAG-LLM Framework

This guide explains how to resolve memory issues in the RAG-LLM Framework by switching to a smaller LLM model.

## Problem Description

The default LLM model (llama2) requires 8.4 GiB of memory, which may exceed available resources on some systems. This results in an error like:

```
ERROR:src.backend.rag_engine:Error querying RAG system: Ollama call failed with status code 500. 
Details: {"error":"model requires more system memory (8.4 GiB) than is available (2.6 GiB)"}
```

## Solution Overview

The solution is to use a smaller model like `tinyllama`, which requires only about 1.2 GiB of memory.

## Fix for Local Development

### Option 1: Using the Automated Script

1. Run the fix script:
   ```bash
   chmod +x scripts/fix-memory-issue.sh
   ./scripts/fix-memory-issue.sh
   ```

2. Pull the tinyllama model:
   ```bash
   ollama pull tinyllama
   ```

3. Run the application:
   ```bash
   ./scripts/run-local-native.sh
   ```

### Option 2: Using the Small Model Script

1. Run the small model script:
   ```bash
   chmod +x scripts/run-local-native-small-model.sh
   ./scripts/run-local-native-small-model.sh
   ```

## Fix for Kubernetes Deployment

1. Run the Kubernetes model update script:
   ```bash
   chmod +x scripts/update-k8s-model.sh
   ./scripts/update-k8s-model.sh [namespace] [release-name]
   ```
   
   Default values:
   - namespace: rag-llm
   - release-name: rag-llm-framework

2. Verify the deployment:
   ```bash
   kubectl get pods -n rag-llm
   kubectl logs -f deployment/rag-llm-backend -n rag-llm
   ```

## Manual Configuration

### Local Development

1. Edit `config/config.yaml`:
   ```yaml
   llm:
     ollama:
       model_name: tinyllama  # Change from llama2 to tinyllama
   ```

2. Set the environment variable in your `.env` file:
   ```
   OLLAMA_MODEL_NAME=tinyllama
   ```

3. Pull the model:
   ```bash
   ollama pull tinyllama
   ```

### Kubernetes Deployment

1. Update Helm values:
   ```bash
   helm upgrade rag-llm-framework ./helm/rag-llm-framework \
     --namespace rag-llm \
     --set backend.config.llm.ollama.model_name=tinyllama \
     --set ollama.resources.limits.memory=2Gi \
     --set ollama.resources.requests.memory=1Gi
   ```

## Model Comparison

| Model | Memory Required | Recommended System Memory |
|-------|----------------|--------------------------|
| llama2 | 8.4 GiB | 12+ GiB |
| tinyllama | 1.2 GiB | 4+ GiB |
| orca-mini | 2.0 GiB | 4+ GiB |
| phi | 1.7 GiB | 4+ GiB |

## Performance Considerations

Smaller models generally offer:
- Faster inference times
- Lower memory usage
- Reduced accuracy compared to larger models

Choose the model that best balances your memory constraints and performance requirements.

## Troubleshooting

If you still encounter memory issues:
1. Close other memory-intensive applications
2. Restart the Ollama service
3. Try reducing the context window size in your configuration
4. Consider using a swap file to extend available memory (not recommended for production)

For more detailed information on model memory requirements, see [memory-requirements.md](memory-requirements.md).
