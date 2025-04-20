# Container Troubleshooting Guide

This guide provides solutions for common issues encountered when running the RAG-LLM Framework in Docker containers.

## CPU Allocation Issues

If you encounter this error:
```
Error response from daemon: Range of CPUs is from 0.01 to 2.00, as there are only 2 CPUs available
```

**Solution**: Edit `docker-compose.yml` to reduce CPU allocation:
```yaml
deploy:
  resources:
    limits:
      memory: 4G
      cpus: '1.5'  # Reduce this to 2 or less
```

## Container Restart Loops

If containers keep restarting:

1. **Check logs**:
   ```bash
   docker logs <container_id>
   ```

2. **Disable restart policy** for debugging:
   ```yaml
   # Change from
   restart: unless-stopped
   # To
   restart: "no"
   ```

3. **Run in foreground** to see errors:
   ```bash
   docker-compose up backend
   ```

## Import Errors

If you see `ModuleNotFoundError: No module named 'rag_engine'`:

1. **Mount source code** in docker-compose.yml:
   ```yaml
   volumes:
     - ./src:/app/src
   ```

2. **Set PYTHONPATH**:
   ```yaml
   environment:
     - PYTHONPATH=/app
   ```

3. **Use explicit module path**:
   ```yaml
   command: ["sh", "-c", "cd /app && python -m src.backend.main"]
   ```

## Ollama Connection Issues

If the backend can't connect to Ollama:

1. **Verify Ollama is running**:
   ```bash
   docker ps | grep ollama
   ```

2. **Check network connectivity**:
   ```bash
   docker exec -it <backend_container_id> curl -v http://ollama:11434/api/tags
   ```

3. **Ensure correct URL**:
   ```yaml
   environment:
     - OLLAMA_BASE_URL=http://ollama:11434
   ```

4. **Check healthcheck status**:
   ```bash
   docker inspect --format='{{json .State.Health}}' <ollama_container_id> | jq
   ```

5. **Ensure backend waits for Ollama**:
   ```yaml
   depends_on:
     ollama:
       condition: service_healthy
   ```

## Resource Constraints

For machines with limited resources:

1. **Reduce memory allocation**:
   ```yaml
   deploy:
     resources:
       limits:
         memory: 12G  # Default allocation
         cpus: '1.5'  # Default CPU allocation
   ```

   For machines with less memory:
   ```yaml
   deploy:
     resources:
       limits:
         memory: 4G  # Reduce as needed
         cpus: '1.0'  # Reduce as needed
   ```

2. **Use smaller models** in config.yaml:
   ```yaml
   llm:
     ollama:
       model_name: tinyllama  # Use a smaller model
   ```

## Debugging Container Internals

To debug inside a container:

1. **Shell into container**:
   ```bash
   docker exec -it <container_id> /bin/bash
   ```

2. **Test imports**:
   ```bash
   cd /app
   python -c "from src.backend.rag_engine import RAGEngine; print('Import successful')"
   ```

3. **Check environment variables**:
   ```bash
   env | grep PYTHON
   ```

4. **Verify file structure**:
   ```bash
   ls -la /app/src/backend/
   ```
