# Complete Memory Fix Guide for RAG-LLM Framework

This guide provides comprehensive instructions for resolving memory issues in the RAG-LLM Framework by switching to a smaller LLM model.

## Problem Description

The default LLM model (llama2) requires 8.4 GiB of memory, which may exceed available resources on some systems. This results in an error like:

```
ERROR:src.backend.rag_engine:Error querying RAG system: Ollama call failed with status code 500. 
Details: {"error":"model requires more system memory (8.4 GiB) than is available (2.6 GiB)"}
```

## Solution Overview

The solution is to use a smaller model like `tinyllama`, which requires only about 1.2 GiB of memory.

## Step 1: Install Ollama

Ollama is required to run the LLM models. If it's not already installed:

```bash
# Make the script executable
chmod +x scripts/install-ollama.sh

# Run the installation script
./scripts/install-ollama.sh
```

For manual installation instructions, see [ollama-installation.md](ollama-installation.md).

## Step 2: Apply the Memory Fix

### Option 1: Using the Automated Script (Recommended)

```bash
# Make the script executable
chmod +x scripts/fix-memory-issue.sh

# Run the fix script
./scripts/fix-memory-issue.sh
```

This script will:
- Update config.yaml to use tinyllama model
- Update .env file with the correct model
- Modify run-local-native.sh to use tinyllama
- Pull the tinyllama model if Ollama is installed

### Option 2: Using the Small Model Script

```bash
# Make the script executable
chmod +x scripts/run-local-native-small-model.sh

# Run the application with the small model
./scripts/run-local-native-small-model.sh
```

### Option 3: Manual Configuration

1. Edit `config/config.yaml`:
   ```yaml
   llm:
     provider: "ollama"
     model: "tinyllama"  # Change from llama2 to tinyllama
   ```

2. Set the environment variable in your `.env` file:
   ```
   OLLAMA_MODEL_NAME=tinyllama
   ```

3. Pull the model:
   ```bash
   ollama pull tinyllama
   ```

## Step 3: Verify the Fix

```bash
# Make the script executable
chmod +x scripts/verify-model.sh

# Run the verification script
./scripts/verify-model.sh
```

This script will:
- Check if Ollama is installed
- Verify the Ollama service is running
- List available models
- Check the current model in the configuration
- Display system memory information

## For Kubernetes Deployment

If you're using Kubernetes, you can update your deployment with:

```bash
# Make the script executable
chmod +x scripts/update-k8s-model.sh

# Run the update script
./scripts/update-k8s-model.sh
```

This will update your Helm deployment to use the tinyllama model and adjust memory limits.

## Model Comparison

| Model | Memory Required | Recommended System Memory |
|-------|----------------|--------------------------|
| llama2 | 8.4 GiB | 12+ GiB |
| tinyllama | 1.2 GiB | 4+ GiB |
| orca-mini | 2.0 GiB | 4+ GiB |
| phi | 1.7 GiB | 4+ GiB |

## Troubleshooting

If you still encounter memory issues:
1. Close other memory-intensive applications
2. Restart the Ollama service
3. Try reducing the context window size in your configuration
4. Consider using a swap file to extend available memory (not recommended for production)

For more detailed information on model memory requirements, see [memory-requirements.md](memory-requirements.md).
