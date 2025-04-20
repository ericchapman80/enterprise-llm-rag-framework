# Troubleshooting Guide for RAG-LLM Framework

This guide provides solutions for common issues you might encounter when deploying and running the RAG-LLM Framework.

## Backend Pod in Pending State

If your backend pod is stuck in a pending state, it's likely due to insufficient CPU resources.

### Symptoms
- Backend pod shows status "Pending" in `kubectl get pods -n rag-llm`
- No logs available from the backend pod
- When describing the pod, you see "FailedScheduling" events with "Insufficient cpu" messages

### Solution
We've provided a script to fix this issue by reducing the CPU and memory requirements:

```bash
# Make the script executable
chmod +x scripts/fix-resource-limits.sh

# Run the script
./scripts/fix-resource-limits.sh
```

Alternatively, you can use the Makefile target:

```bash
make fix-resources
```

This will update the Helm deployment with reduced resource requirements that should work on most development machines.

## Backend Health Endpoint Not Accessible

If you can access Ollama at http://localhost:11434/ but the backend health endpoint at http://rag-llm.local/health is not working, there could be several issues.

### Symptoms
- Ollama is running and accessible
- Backend health endpoint returns an error or is not accessible
- Backend pod might be running but the application inside is failing

### Solutions

1. **Check if the backend pod is running:**
   ```bash
   kubectl get pods -n rag-llm -l app=rag-llm-backend
   ```

2. **Check the backend pod logs for errors:**
   ```bash
   kubectl logs -n rag-llm -l app=rag-llm-backend
   ```

3. **Verify the ingress configuration:**
   ```bash
   kubectl get ingress -n rag-llm
   ```

4. **Check if the host is properly configured in your /etc/hosts file:**
   ```bash
   cat /etc/hosts | grep rag-llm.local
   ```
   
   If missing, run:
   ```bash
   make configure-hosts
   ```

5. **If you see import errors in the logs** like `ModuleNotFoundError: No module named 'rag_engine'`, we've created a dedicated fix:
   ```bash
   make fix-import
   ```
   
   This will:
   - Update main.py with robust import handling
   - Rebuild the Docker image
   - Redeploy the backend pod
   
   Alternatively, you can manually rebuild and redeploy:
   ```bash
   make build
   make deploy
   ```

6. **Test the backend directly using port-forwarding:**
   ```bash
   kubectl port-forward -n rag-llm svc/rag-llm-backend 8000:8000
   curl http://localhost:8000/health
   ```

## Ollama Model Not Loading

If Ollama is running but the model is not loading or responding to queries:

### Symptoms
- Ollama pod is running
- Queries to the backend return errors about the model not being available

### Solutions

1. **Check if the model is downloaded:**
   ```bash
   kubectl exec -it -n rag-llm $(kubectl get pod -n rag-llm -l app=ollama -o jsonpath='{.items[0].metadata.name}') -- ollama list
   ```

2. **Pull the model manually:**
   ```bash
   make pull-model
   ```

3. **Check Ollama logs for errors:**
   ```bash
   kubectl logs -n rag-llm -l app=ollama
   ```

## Comprehensive Troubleshooting Script

We've provided a comprehensive troubleshooting script that can help diagnose issues:

```bash
chmod +x scripts/troubleshoot-backend.sh
./scripts/troubleshoot-backend.sh
```

This script will:
- Check the backend pod status
- Display pod events
- Check ingress configuration
- Check backend service
- Check storage classes
- Provide suggestions for fixing common issues
