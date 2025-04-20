# GitHub Repositories Management

This document explains how to manage GitHub repositories as knowledge sources for the RAG-LLM Framework.

## Configuration File

The framework uses a JSON configuration file to manage GitHub repositories. The default location is:

```
config/github_repos.json
```

You can override this location by setting the `REPOS_CONFIG_PATH` environment variable.

## File Format

The configuration file has the following structure:

```json
{
  "repositories": [
    {
      "repo_url": "https://github.com/your-org/your-repo",
      "branch": "main",
      "file_extensions": [".md", ".py", ".js"],
      "description": "Description of the repository"
    },
    {
      "repo_url": "https://github.com/your-org/another-repo",
      "branch": "develop",
      "file_extensions": [".md"],
      "description": "Another repository"
    }
  ],
  "auto_ingest_on_startup": true,
  "last_updated": "2025-04-17T16:36:07Z"
}
```

### Fields

- `repositories`: Array of repository configurations
  - `repo_url`: URL of the GitHub repository
  - `branch`: Branch to ingest (default: "main")
  - `file_extensions`: Array of file extensions to include (default: [".md", ".py", ".js", ".txt"])
  - `description`: Optional description of the repository
- `auto_ingest_on_startup`: Whether to automatically ingest repositories on startup (default: true)
- `last_updated`: Timestamp of the last update (automatically updated)

## API Endpoints

The framework provides the following API endpoints for managing GitHub repositories:

### List Repositories

```
GET /repos/repos
```

Returns the list of configured GitHub repositories.

### Update Repositories

```
POST /repos/update-repos
```

Updates the list of GitHub repositories.

Request body:
```json
{
  "repositories": [
    {
      "repo_url": "https://github.com/your-org/your-repo",
      "branch": "main",
      "file_extensions": [".md", ".py", ".js"],
      "description": "Description of the repository"
    }
  ],
  "auto_ingest_on_startup": true
}
```

### Ingest GitHub Repository

```
POST /repos/ingest/github
```

Ingests a GitHub repository into the RAG system.

Request body:
```json
{
  "repo_url": "https://github.com/your-org/your-repo",
  "branch": "main",
  "file_extensions": [".md", ".py", ".js"]
}
```

### Ingest All Repositories

```
POST /repos/ingest-repos
```

Ingests all repositories configured in the repository configuration file.

## Scheduled Updates

You can set up a cron job to periodically update the knowledge base with the latest content from the configured GitHub repositories.

The framework includes a script for this purpose:

```bash
scripts/refresh-github-repos.sh
```

Example cron job (runs every day at 2 AM):

```
0 2 * * * /path/to/rag-llm-framework/scripts/refresh-github-repos.sh >> /path/to/rag-llm-framework/logs/github-refresh.log 2>&1
```

Make sure the script is executable:

```bash
chmod +x scripts/refresh-github-repos.sh
```

## Authentication

GitHub API access requires authentication. The framework uses a GitHub personal access token for this purpose.

Set the `GITHUB_TOKEN` environment variable in your `.env` file:

```
GITHUB_TOKEN=your_github_token_here
```

The token needs the following permissions:
- `repo` (for private repositories)
- `public_repo` (for public repositories)
