# GitHub Repository Ingestion Guide

This guide explains how to use the GitHub repository ingestion endpoint to add markdown files and other content as context for the RAG-LLM Framework.

## Overview

The GitHub ingestion endpoint allows you to ingest content from GitHub repositories into the RAG-LLM Framework's vector database. This is particularly useful for adding documentation, code examples, and other text-based content as context for the RAG system.

## Prerequisites

Before using the GitHub ingestion endpoint, ensure:

1. The RAG-LLM Framework backend is running
2. You have set the `GITHUB_TOKEN` environment variable (required for private repositories)
3. GitPython is installed (`pip install GitPython`)

## Setting the GitHub Token

The GitHub token is required for accessing private repositories. You can set it in your `.env` file:

```
GITHUB_TOKEN=your_github_token_here
```

Or set it directly in your environment:

```bash
export GITHUB_TOKEN=your_github_token_here
```

## Using the GitHub Ingestion Endpoint

### Endpoint Details

- **URL**: `/ingest/github`
- **Method**: POST
- **Content-Type**: application/json

### Request Parameters

| Parameter | Type | Description | Required | Default |
|-----------|------|-------------|----------|---------|
| repo_url | string | URL of the GitHub repository to ingest | Yes | - |
| branch | string | Branch name to ingest | No | main |
| file_extensions | array/string | File extensions to include | No | [".md", ".py", ".js", ".txt"] |

### Example Request

```bash
curl -X POST http://localhost:8000/ingest/github \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/username/repository",
    "branch": "main",
    "file_extensions": [".md"]
  }'
```

To ingest only markdown files from a specific repository:

```bash
curl -X POST http://localhost:8000/ingest/github \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/wwg-internal/productcore-launchpoint",
    "branch": "main",
    "file_extensions": [".md"]
  }'
```

### Response

A successful response will look like:

```json
{
  "status": "success",
  "message": "Successfully ingested 42 documents from GitHub repository",
  "document_count": 42
}
```

## Verifying Ingestion

After ingesting a repository, you can verify the ingested data using the following endpoints:

1. List ingested data sources:
   ```bash
   curl http://localhost:8000/ingested
   ```

2. View ingested documents:
   ```bash
   curl http://localhost:8000/ingested-data
   ```

3. Test a query with the ingested context:
   ```bash
   curl -X POST http://localhost:8000/query-comparison \
     -H "Content-Type: application/json" \
     -d '{"query": "What is the purpose of the productcore-launchpoint repository?"}'
   ```

## Troubleshooting

### Common Errors

1. **Missing GitHub Token**:
   ```
   Error ingesting GitHub repository: Authentication required for private repository
   ```
   Solution: Set the `GITHUB_TOKEN` environment variable.

2. **Missing GitPython**:
   ```
   Error ingesting GitHub repo: Could not import git python package. Please install it with `pip install GitPython`.
   ```
   Solution: Install GitPython with `pip install GitPython`.

3. **Repository Not Found**:
   ```
   Error ingesting GitHub repository: Repository not found
   ```
   Solution: Verify the repository URL and your access permissions.

## Ingestion Process

When you ingest a GitHub repository:

1. The system clones the repository to a temporary directory
2. It filters files based on the specified file extensions
3. Each file is processed and split into chunks
4. The chunks are embedded and stored in the vector database
5. The repository metadata is preserved for source attribution

This allows the RAG system to retrieve relevant information from the repository when answering queries.
