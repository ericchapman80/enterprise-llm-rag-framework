# Model Storage Configuration

This document explains how to configure different storage options for LLM models in the RAG-LLM Framework.

## Overview

The RAG-LLM Framework supports multiple storage options for LLM models:

1. **Local Storage** (default): Models are downloaded and stored locally in the container
2. **Cloud Storage**: Models are stored in cloud storage (S3, GCS, Azure Blob Storage)
3. **Network File System (NFS)**: Models are stored on a shared NFS volume

Using cloud storage or NFS can significantly improve container startup times and resource utilization during scaling events, as models don't need to be downloaded for each container instance.

## Configuration Options

### Environment Variables

You can configure model storage using the following environment variables:

```
# Model Storage Configuration
OLLAMA_STORAGE_TYPE=local  # Options: local, cloud
OLLAMA_CLOUD_PROVIDER=s3   # Options: s3, gcs, azure, nfs
OLLAMA_CACHE_DIR=/tmp/ollama_cache

# S3 Configuration (when OLLAMA_CLOUD_PROVIDER=s3)
S3_BUCKET=your-models-bucket
S3_REGION=us-west-2
S3_PREFIX=models/
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key

# GCS Configuration (when OLLAMA_CLOUD_PROVIDER=gcs)
GCS_BUCKET=your-models-bucket
GCS_PREFIX=models/
GCS_CREDENTIALS_FILE=/path/to/credentials.json

# Azure Configuration (when OLLAMA_CLOUD_PROVIDER=azure)
AZURE_CONTAINER=your-container
AZURE_STORAGE_ACCOUNT=your-account
AZURE_STORAGE_KEY=your-key

# NFS Configuration (when OLLAMA_CLOUD_PROVIDER=nfs)
NFS_PATH=/mnt/nfs/models
```

### Configuration File

You can also configure model storage in the `config/config.yaml` file:

```yaml
llm:
  ollama:
    base_url: http://localhost:11434
    model_name: llama2
    parameters:
      temperature: 0.7
      top_p: 0.9
      max_tokens: 2048
    storage:
      type: local  # Options: local, cloud
      cloud:
        provider: s3  # Options: s3, gcs, azure, nfs
        s3:
          bucket: ""
          region: ""
          prefix: "models/"
          access_key: "${S3_ACCESS_KEY}"
          secret_key: "${S3_SECRET_KEY}"
        gcs:
          bucket: ""
          prefix: "models/"
          credentials_file: "${GCS_CREDENTIALS_FILE}"
        azure:
          container: ""
          account: ""
          key: "${AZURE_STORAGE_KEY}"
        nfs:
          server: ""
          path: "/models"
      cache:
        enabled: true
        size: "5Gi"
        ttl: "24h"
```

## Storage Types

### Local Storage (Default)

With local storage, models are downloaded and stored within the container. This is the simplest option but has some drawbacks:

- Each container instance needs to download the model, which can be time-consuming
- Requires more disk space as each container has its own copy of the model
- Slower startup times for new container instances

### Cloud Storage

Cloud storage options allow models to be stored in cloud object storage services:

#### Amazon S3

To use Amazon S3:

1. Set `OLLAMA_STORAGE_TYPE=cloud` and `OLLAMA_CLOUD_PROVIDER=s3`
2. Configure S3 bucket details:
   ```
   S3_BUCKET=your-models-bucket
   S3_REGION=us-west-2
   S3_PREFIX=models/
   S3_ACCESS_KEY=your-access-key
   S3_SECRET_KEY=your-secret-key
   ```

#### Google Cloud Storage (GCS)

To use Google Cloud Storage:

1. Set `OLLAMA_STORAGE_TYPE=cloud` and `OLLAMA_CLOUD_PROVIDER=gcs`
2. Configure GCS bucket details:
   ```
   GCS_BUCKET=your-models-bucket
   GCS_PREFIX=models/
   GCS_CREDENTIALS_FILE=/path/to/credentials.json
   ```

#### Azure Blob Storage

To use Azure Blob Storage:

1. Set `OLLAMA_STORAGE_TYPE=cloud` and `OLLAMA_CLOUD_PROVIDER=azure`
2. Configure Azure container details:
   ```
   AZURE_CONTAINER=your-container
   AZURE_STORAGE_ACCOUNT=your-account
   AZURE_STORAGE_KEY=your-key
   ```

### Network File System (NFS)

To use a shared NFS volume:

1. Set `OLLAMA_STORAGE_TYPE=cloud` and `OLLAMA_CLOUD_PROVIDER=nfs`
2. Configure NFS path:
   ```
   NFS_PATH=/mnt/nfs/models
   ```

## Kubernetes Configuration

For Kubernetes deployments, you can configure model storage in the Helm values:

```yaml
ollama:
  persistence:
    enabled: true
    size: 20Gi
    storageClass: ""
    storage:
      type: local  # Options: local, cloud
      cloud:
        provider: s3  # Options: s3, gcs, azure, nfs
        s3:
          bucket: ""
          region: ""
          prefix: "models/"
          secretName: ""  # Name of the Kubernetes secret containing S3 credentials
        gcs:
          bucket: ""
          prefix: "models/"
          secretName: ""  # Name of the Kubernetes secret containing GCS credentials
        azure:
          container: ""
          account: ""
          secretName: ""  # Name of the Kubernetes secret containing Azure credentials
        nfs:
          server: ""
          path: "/models"
      cache:
        enabled: true
        size: "5Gi"
        ttl: "24h"
```

## Using the Model Controller

When using cloud storage in Kubernetes, a model controller is deployed to manage model downloads and caching. The model controller:

1. Monitors model usage across pods
2. Pre-downloads frequently used models
3. Manages the model cache to optimize storage usage
4. Handles model updates and versioning

## Makefile Commands

The following Makefile commands are available for model storage configuration:

```bash
# Configure storage type
make configure-storage STORAGE_TYPE=cloud CLOUD_PROVIDER=s3

# Build model controller Docker image
make build-model-controller

# Deploy with cloud storage configuration
make deploy-cloud-storage
```

## Benefits of Cloud Storage

Using cloud storage for LLM models provides several benefits:

1. **Faster container startup**: Containers don't need to download the entire model
2. **Reduced disk usage**: Only one copy of the model is needed
3. **Efficient scaling**: New pods can start quickly without downloading models
4. **Centralized management**: Models can be updated in one place
5. **Cost optimization**: Reduced storage and bandwidth costs

## Caching Mechanism

The framework implements a caching mechanism for cloud storage:

1. Frequently used models are cached locally
2. Cache size and TTL (time-to-live) are configurable
3. Least recently used (LRU) eviction policy is used when cache is full
4. Cache is shared across pods when using NFS

## Troubleshooting

If you encounter issues with model storage:

1. Check that the cloud credentials are correct
2. Verify that the bucket/container exists and is accessible
3. Check that the model controller pod is running (for Kubernetes deployments)
4. Inspect the model controller logs for errors:
   ```bash
   kubectl logs -f deployment/rag-llm-model-controller -n rag-llm
   ```
5. Verify that the cache directory is writable
