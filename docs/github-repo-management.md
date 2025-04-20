# GitHub Repository Management

This document explains how to use the GitHub repository management features of the RAG-LLM Framework.

## Overview

The RAG-LLM Framework provides a mechanism to manage GitHub repositories that are ingested into the RAG system. This allows you to:

1. Configure a list of GitHub repositories to be ingested automatically on startup
2. Update the repository list via an API endpoint
3. Manually trigger ingestion of all configured repositories

## Configuration File

The GitHub repositories are configured in a JSON file located at `config/repos.json`. This file has the following structure:

```json
{
  "repositories": [
    {
      "repo_url": "https://github.com/example/repo1",
      "branch": "main",
      "file_extensions": [".md", ".py", ".js"],
      "description": "Example repository 1"
    },
    {
      "repo_url": "https://github.com/example/repo2",
      "branch": "develop",
      "file_extensions": [".md"],
      "description": "Example repository 2"
    }
  ],
  "auto_ingest_on_startup": true,
  "last_updated": "2025-04-15T05:34:35Z"
}
```

### Configuration Options

- `repositories`: An array of repository objects with the following properties:
  - `repo_url`: The URL of the GitHub repository
  - `branch`: The branch to ingest (defaults to "main")
  - `file_extensions`: An array of file extensions to include (defaults to [".md", ".py", ".js", ".txt"])
  - `description`: An optional description of the repository
- `auto_ingest_on_startup`: Whether to automatically ingest all repositories on startup (defaults to true)
- `last_updated`: The timestamp when the configuration was last updated (automatically set by the system)

## API Endpoints

The following API endpoints are available for managing GitHub repositories:

### List Repositories

```
GET /repos/repos
```

Returns the current repository configuration.

Example response:

```json
{
  "repositories": [
    {
      "repo_url": "https://github.com/example/repo1",
      "branch": "main",
      "file_extensions": [".md", ".py", ".js"],
      "description": "Example repository 1"
    }
  ],
  "auto_ingest_on_startup": true,
  "last_updated": "2025-04-15T05:34:35Z"
}
```

### Update Repositories

```
POST /repos/update-repos
```

Updates the repository configuration with a new list of repositories.

Example request:

```json
{
  "repositories": [
    {
      "repo_url": "https://github.com/example/repo1",
      "branch": "main",
      "file_extensions": [".md", ".py", ".js"],
      "description": "Example repository 1"
    },
    {
      "repo_url": "https://github.com/example/repo2",
      "branch": "develop",
      "file_extensions": [".md"],
      "description": "Example repository 2"
    }
  ],
  "auto_ingest_on_startup": true
}
```

Example response:

```json
{
  "status": "success",
  "message": "Successfully updated repository configuration with 2 repositories",
  "repositories": [
    {
      "repo_url": "https://github.com/example/repo1",
      "branch": "main",
      "file_extensions": [".md", ".py", ".js"],
      "description": "Example repository 1"
    },
    {
      "repo_url": "https://github.com/example/repo2",
      "branch": "develop",
      "file_extensions": [".md"],
      "description": "Example repository 2"
    }
  ]
}
```

### Ingest All Repositories

```
POST /repos/ingest-repos
```

Triggers ingestion of all repositories configured in the repository configuration file.

Example response:

```json
{
  "status": "success",
  "message": "Ingestion completed with 2 successful and 0 failed repositories",
  "results": {
    "success": [
      {
        "repo_url": "https://github.com/example/repo1",
        "branch": "main",
        "document_count": 15
      },
      {
        "repo_url": "https://github.com/example/repo2",
        "branch": "develop",
        "document_count": 8
      }
    ],
    "failed": []
  }
}
```

## Setting Up a Cron Job

You can set up a cron job to periodically update the repositories by calling the `/repos/ingest-repos` endpoint. This allows you to keep your RAG system up-to-date with the latest changes in your GitHub repositories.

Example cron job (runs every hour):

```bash
0 * * * * curl -X POST http://your-server:8000/repos/ingest-repos
```

## Environment Variables

The following environment variables can be used to configure the GitHub repository management:

- `REPOS_CONFIG_PATH`: The path to the repository configuration file (defaults to "config/repos.json")
- `GITHUB_TOKEN`: The GitHub API token used for accessing private repositories

## Startup Behavior

When the RAG-LLM Framework starts up, it will automatically ingest all repositories configured in the repository configuration file if `auto_ingest_on_startup` is set to `true`. This behavior can be disabled by setting `auto_ingest_on_startup` to `false` in the configuration file.
