# Memory Requirements for LLM Models

This document outlines the memory requirements for different LLM models used in the RAG-LLM Framework and provides guidance on selecting the appropriate model based on available system resources.

## Memory Requirements by Model

| Model | Memory Required | Recommended System Memory |
|-------|----------------|--------------------------|
| llama2 | 8.4 GiB | 12+ GiB |
| tinyllama | 1.2 GiB | 4+ GiB |
| orca-mini | 2.0 GiB | 4+ GiB |
| phi | 1.7 GiB | 4+ GiB |
| mistral | 4.1 GiB | 8+ GiB |

## Memory Error Diagnosis

If you encounter an error like:

```
ERROR:src.backend.rag_engine:Error querying RAG system: Ollama call failed with status code 500. Details: {"error":"model requires more system memory (8.4 GiB) than is available (2.6 GiB)"}
```

This indicates that the model you're trying to use (in this case, llama2) requires more memory than your system has available.

## Solutions

### 1. Use a Smaller Model

For systems with limited memory (less than 8 GiB), use one of these smaller models:

- **tinyllama**: Best for very memory-constrained environments (requires ~1.2 GiB)
- **phi**: Good balance of performance and memory usage (requires ~1.7 GiB)
- **orca-mini**: Another good option for 4 GiB systems (requires ~2.0 GiB)

To use a smaller model:

```bash
# Pull the smaller model
ollama pull tinyllama

# Update your .env file
echo "OLLAMA_MODEL_NAME=tinyllama" >> .env

# Or use the small model script
./scripts/run-local-native-small-model.sh
```

### 2. Increase Available Memory

If you're running in Docker or Kubernetes:

- **Docker Compose**: Update memory limits in `docker-compose.yml`:
  ```yaml
  ollama:
    deploy:
      resources:
        limits:
          memory: 12G  # Increase from default
  ```

- **Kubernetes**: Update memory limits in Helm values:
  ```yaml
  ollama:
    resources:
      limits:
        memory: 12Gi  # Increase from default
  ```

### 3. Use Cloud-Hosted Models

For production environments with memory constraints, consider using cloud-hosted models through APIs like:
- OpenAI API
- Anthropic Claude API
- Hugging Face Inference API

## Performance Considerations

Smaller models generally offer:
- Faster inference times
- Lower memory usage
- Reduced accuracy compared to larger models

Choose the model that best balances your memory constraints and performance requirements.

## Monitoring Memory Usage

To monitor memory usage:

```bash
# Check system memory
free -h

# Check Ollama process memory
ps -o pid,user,%mem,command ax | grep ollama
```

## Troubleshooting

If you continue to experience memory issues:
1. Close other memory-intensive applications
2. Restart the Ollama service
3. Try reducing the context window size in your configuration
4. Consider using a swap file to extend available memory (not recommended for production)
