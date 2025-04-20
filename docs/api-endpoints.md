# RAG-LLM Framework API Endpoints

This document describes the API endpoints available in the RAG-LLM Framework, which provides Retrieval Augmented Generation (RAG) capabilities for enhancing LLM responses with relevant context from your knowledge base.

## Core Endpoints

### Health Check

```
GET /health
```

Returns the health status of the API. Use this endpoint to verify that the API is running correctly and to check the current version.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

**Usage Example:**
```bash
curl -X GET http://localhost:8000/health
```

**Common Error Codes:**
- `500 Internal Server Error`: The server is experiencing issues

### Query

```
POST /query
```

Query the RAG-LLM system with a question or prompt. This endpoint retrieves relevant information from your knowledge base and uses it to generate a more informed response from the LLM.

**Request Body Parameters:**
- `query` (string, required): The question or prompt to send to the RAG system
- `max_tokens` (integer, optional): Maximum number of tokens to generate in the response
- `temperature` (float, optional): Controls randomness in the response (0.0-1.0)

**Request Body Example:**
```json
{
  "query": "What is RAG?",
  "max_tokens": 500,
  "temperature": 0.7
}
```

**Response:**
```json
{
  "response": "RAG (Retrieval Augmented Generation) is a technique that enhances large language models by retrieving relevant information from external knowledge sources before generating a response...",
  "sources": [
    {
      "content": "Retrieval Augmented Generation (RAG) is an AI framework that enhances large language model outputs by using a retrieval system to fetch relevant information from a knowledge base...",
      "metadata": {
        "source": "documentation.md",
        "page": 1
      }
    }
  ]
}
```

**Usage Example:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is RAG?", "max_tokens": 500, "temperature": 0.7}'
```

**Common Error Codes:**
- `400 Bad Request`: Missing or invalid query parameter
- `500 Internal Server Error`: Error processing the query or connecting to the LLM

### Feedback

```
POST /feedback
```

Submit feedback for a query response. This endpoint allows users to provide feedback on the quality and relevance of responses, which can be used to improve the system over time.

**Request Body Parameters:**
- `query_id` (string, required): Identifier for the query that received the feedback
- `feedback` (string, required): The feedback text
- `details` (string, optional): Additional details about the feedback
- `rating` (integer, optional): Numerical rating (e.g., 1-5)

**Request Body Example:**
```json
{
  "query_id": "123456",
  "feedback": "This response was very helpful and accurate.",
  "details": "The sources provided were particularly relevant.",
  "rating": 5
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Feedback submitted successfully"
}
```

**Usage Example:**
```bash
curl -X POST http://localhost:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{"query_id": "123456", "feedback": "This response was very helpful and accurate.", "rating": 5}'
```

**Common Error Codes:**
- `400 Bad Request`: Missing required parameters
- `500 Internal Server Error`: Error storing the feedback

## Data Ingestion Endpoints

### Ingest Data

```
POST /ingest
```

Ingest data into the RAG system. This endpoint allows you to add text content to the knowledge base that will be used for retrieval during queries.

**Request Body Parameters:**
- `source_type` (string, required): Type of data being ingested (e.g., "text", "markdown", "code")
- `source_data` (string, required): The actual content to be ingested
- `metadata` (object, optional): Additional metadata about the content

**Request Body Example:**
```json
{
  "source_type": "text",
  "source_data": "This is some text data to be ingested into the RAG system.",
  "metadata": {
    "source": "internal-documentation",
    "author": "engineering-team",
    "date": "2025-04-17"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Data ingestion started"
}
```

**Usage Example:**
```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "text",
    "source_data": "This is some text data to be ingested into the RAG system.",
    "metadata": {
      "source": "internal-documentation",
      "author": "engineering-team"
    }
  }'
```

**Common Error Codes:**
- `400 Bad Request`: Missing required parameters
- `500 Internal Server Error`: Error processing or storing the data

### Ingest GitHub Repository

```
POST /ingest/github
```

Ingest a GitHub repository into the RAG system. This endpoint will clone the repository and process all files matching the specified file extensions, making their content available for retrieval during queries.

**Request Body Parameters:**
- `repo_url` (string, required): URL of the GitHub repository to ingest
- `branch` (string, optional): Branch to ingest, defaults to "main"
- `file_extensions` (array, optional): List of file extensions to process, defaults to [".md", ".py", ".js", ".txt"]

**Request Body Example:**
```json
{
  "repo_url": "https://github.com/username/repository",
  "branch": "main",
  "file_extensions": [".md", ".py", ".js", ".txt"]
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Successfully ingested 42 documents from GitHub repository",
  "document_count": 42
}
```

**Usage Example:**
```bash
curl -X POST http://localhost:8000/ingest/github \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -d '{
    "repo_url": "https://github.com/username/repository",
    "branch": "main",
    "file_extensions": [".md", ".py", ".js", ".txt"]
  }'
```

**Common Error Codes:**
- `400 Bad Request`: Missing or invalid repository URL
- `401 Unauthorized`: Missing or invalid GitHub token
- `404 Not Found`: Repository not found
- `500 Internal Server Error`: Error cloning or processing the repository

**Note:** This endpoint requires the `GITHUB_TOKEN` environment variable to be set for accessing private repositories. For public repositories, the token is still recommended to avoid GitHub API rate limits.

### Ingest All Configured Repositories

```
POST /repos/ingest-repos
```

Ingest all repositories configured in the repository configuration file (config/github_repos.json). This endpoint is useful for refreshing the RAG system's knowledge base with the latest content from all configured repositories.

**Request Body Parameters:**
- None required

**Response:**
```json
{
  "status": "success",
  "message": "Ingestion completed with 2 successful and 0 failed repositories",
  "results": {
    "success": [
      {
        "repo_url": "https://github.com/username/repo1",
        "branch": "main",
        "document_count": 25
      },
      {
        "repo_url": "https://github.com/username/repo2",
        "branch": "main",
        "document_count": 17
      }
    ],
    "failed": []
  }
}
```

**Usage Example:**
```bash
# Set GitHub token in environment
export GITHUB_TOKEN=your_github_token

# Call the endpoint
curl -X POST http://localhost:8000/repos/ingest-repos \
  -H "Content-Type: application/json"
```

**Automation Example:**
```bash
# Add to crontab to refresh repositories daily at 2 AM
0 2 * * * export GITHUB_TOKEN=your_github_token && curl -X POST http://localhost:8000/repos/ingest-repos
```

**Common Error Codes:**
- `500 Internal Server Error`: Error reading configuration or processing repositories

**Note:** This endpoint is designed to be called via a cron job using the provided scripts/refresh-github-repos.sh script for automated updates.

## Data Management Endpoints

### List Ingested Data Sources

```
GET /ingested
```

List all ingested data sources and document counts. This endpoint provides a summary of all data sources that have been ingested into the RAG system, along with the number of documents from each source.

**Response:**
```json
{
  "status": "success",
  "total_documents": 42,
  "sources": {
    "github.com/username/repository": 30,
    "documentation.md": 12
  }
}
```

**Usage Example:**
```bash
curl -X GET http://localhost:8000/ingested
```

**Common Error Codes:**
- `500 Internal Server Error`: Error accessing the vector database

### View Ingested Data

```
GET /ingested-data
```

View all ingested documents with their content and metadata. This endpoint returns detailed information about all documents stored in the vector database, including their content (truncated for readability) and associated metadata.

**Response:**
```json
{
  "status": "success",
  "total_documents": 42,
  "documents": [
    {
      "id": 0,
      "content": "# RAG-LLM Framework\n\nThis framework provides a Retrieval Augmented Generation (RAG) system using Ollama and LangChain...",
      "metadata": {
        "source": "github.com/username/repository/README.md"
      }
    },
    {
      "id": 1,
      "content": "def query(self, query_text: str) -> Dict[str, Any]:\n    \"\"\"Query the RAG system.\"\"\"\n    result = self.qa_chain({\"query\": query_text})...",
      "metadata": {
        "source": "github.com/username/repository/src/backend/rag_engine.py"
      }
    }
  ]
}
```

**Usage Example:**
```bash
curl -X GET http://localhost:8000/ingested-data
```

**Common Error Codes:**
- `500 Internal Server Error`: Error accessing the vector database

### Flush Database

```
POST /flush-database
```

Flush all documents from the vector database. This endpoint removes all documents from the vector database, effectively resetting the RAG system's knowledge base. Use with caution as this operation cannot be undone.

**Response:**
```json
{
  "status": "success",
  "message": "Vector database flushed successfully"
}
```

**Usage Example:**
```bash
curl -X POST http://localhost:8000/flush-database
```

**Common Error Codes:**
- `500 Internal Server Error`: Error flushing the vector database

### List Configured GitHub Repositories

```
GET /repos
```

List all GitHub repositories configured in the system. This endpoint returns the current configuration of GitHub repositories that are set up for ingestion.

**Response:**
```json
{
  "repositories": [
    {
      "repo_url": "https://github.com/username/repository",
      "branch": "main",
      "file_extensions": [".md", ".py"],
      "description": "Repository description"
    }
  ],
  "auto_ingest_on_startup": false,
  "last_updated": "2025-04-17T16:45:07Z"
}
```

**Usage Example:**
```bash
curl -X GET http://localhost:8000/repos
```

**Common Error Codes:**
- `500 Internal Server Error`: Error reading the repository configuration file

### Update GitHub Repository List

```
POST /update-repos
```

Update the list of GitHub repositories configured for ingestion. This endpoint allows you to modify the repository configuration file with new repositories or update existing ones.

**Request Body Parameters:**
- `repositories` (array, required): List of repository configurations
- `auto_ingest_on_startup` (boolean, optional): Whether to automatically ingest repositories on API startup

**Request Body Example:**
```json
{
  "repositories": [
    {
      "repo_url": "https://github.com/username/repository1",
      "branch": "main",
      "file_extensions": [".md", ".py"],
      "description": "First repository"
    },
    {
      "repo_url": "https://github.com/username/repository2",
      "branch": "develop",
      "file_extensions": [".md", ".js"],
      "description": "Second repository"
    }
  ],
  "auto_ingest_on_startup": true
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Repository configuration updated successfully",
  "repository_count": 2
}
```

**Usage Example:**
```bash
curl -X POST http://localhost:8000/update-repos \
  -H "Content-Type: application/json" \
  -d '{
    "repositories": [
      {
        "repo_url": "https://github.com/username/repository1",
        "branch": "main",
        "file_extensions": [".md", ".py"],
        "description": "First repository"
      },
      {
        "repo_url": "https://github.com/username/repository2",
        "branch": "develop",
        "file_extensions": [".md", ".js"],
        "description": "Second repository"
      }
    ],
    "auto_ingest_on_startup": true
  }'
```

**Common Error Codes:**
- `400 Bad Request`: Invalid repository configuration
- `500 Internal Server Error`: Error updating the repository configuration file

## Chat Endpoints

### Send Chat Message

```
POST /chat/send
```

Send a message to the chat system. This endpoint allows for conversational interactions with the RAG-enhanced LLM, maintaining context across multiple messages in a conversation.

**Request Body Parameters:**
- `message` (string, required): The message to send to the chat system
- `conversation_id` (string, optional): Identifier for the conversation, will be generated if not provided
- `max_tokens` (integer, optional): Maximum number of tokens to generate in the response
- `temperature` (float, optional): Controls randomness in the response (0.0-1.0)

**Request Body Example:**
```json
{
  "message": "What are the key features of RAG systems?",
  "conversation_id": "conv-123456",
  "max_tokens": 500,
  "temperature": 0.7
}
```

**Response:**
```json
{
  "conversation_id": "conv-123456",
  "response": "The key features of RAG (Retrieval Augmented Generation) systems include: 1) Contextual retrieval of relevant information from a knowledge base, 2) Integration of retrieved information with LLM generation capabilities, 3) Ability to cite sources for generated content...",
  "sources": [
    {
      "content": "# RAG Features\n\nRetrieval Augmented Generation systems combine the power of retrieval systems with generative AI...",
      "metadata": {
        "source": "documentation.md",
        "page": 3
      }
    }
  ]
}
```

**Usage Example:**
```bash
curl -X POST http://localhost:8000/chat/send \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the key features of RAG systems?",
    "conversation_id": "conv-123456"
  }'
```

**Common Error Codes:**
- `400 Bad Request`: Missing message parameter
- `500 Internal Server Error`: Error processing the message or connecting to the LLM

### Get Chat History

```
GET /chat/history/{conversation_id}
```

Retrieve the history of messages for a specific conversation. This endpoint returns all messages exchanged in a conversation, including both user messages and system responses.

**Path Parameters:**
- `conversation_id` (string, required): Identifier for the conversation to retrieve

**Response:**
```json
{
  "conversation_id": "conv-123456",
  "messages": [
    {
      "role": "user",
      "content": "What are the key features of RAG systems?",
      "timestamp": "2025-04-17T17:30:45Z"
    },
    {
      "role": "assistant",
      "content": "The key features of RAG (Retrieval Augmented Generation) systems include: 1) Contextual retrieval of relevant information from a knowledge base...",
      "timestamp": "2025-04-17T17:30:50Z",
      "sources": [
        {
          "content": "# RAG Features\n\nRetrieval Augmented Generation systems combine the power of retrieval systems with generative AI...",
          "metadata": {
            "source": "documentation.md"
          }
        }
      ]
    }
  ]
}
```

**Usage Example:**
```bash
curl -X GET http://localhost:8000/chat/history/conv-123456
```

**Common Error Codes:**
- `404 Not Found`: Conversation not found
- `500 Internal Server Error`: Error retrieving conversation history

### Submit Chat Feedback

```
POST /chat/feedback
```

Submit feedback for a specific message in a chat conversation. This endpoint allows users to provide feedback on the quality and relevance of chat responses.

**Request Body Parameters:**
- `conversation_id` (string, required): Identifier for the conversation
- `message_idx` (integer, required): Index of the message in the conversation to provide feedback for
- `feedback` (string, required): The feedback text
- `rating` (integer, optional): Numerical rating (e.g., 1-5)

**Request Body Example:**
```json
{
  "conversation_id": "conv-123456",
  "message_idx": 1,
  "feedback": "This response was very helpful and accurate.",
  "rating": 5
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Feedback submitted successfully"
}
```

**Usage Example:**
```bash
curl -X POST http://localhost:8000/chat/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv-123456",
    "message_idx": 1,
    "feedback": "This response was very helpful and accurate.",
    "rating": 5
  }'
```

**Common Error Codes:**
- `400 Bad Request`: Missing required parameters
- `404 Not Found`: Conversation or message not found
- `500 Internal Server Error`: Error storing the feedback

## Demonstration Endpoints

### Query Comparison

```
POST /query-comparison
```

Compare responses with and without RAG context. This endpoint is useful for demonstrating the power of RAG by showing how the model's responses differ when it has access to your specific knowledge base versus when it relies solely on its pre-trained knowledge.

**Request Body Parameters:**
- `query` (string, required): The question or prompt to compare responses for
- `max_tokens` (integer, optional): Maximum number of tokens to generate in the responses
- `temperature` (float, optional): Controls randomness in the responses (0.0-1.0)

**Request Body Example:**
```json
{
  "query": "What is our company's approach to engineering effectiveness?",
  "max_tokens": 500,
  "temperature": 0.7
}
```

**Response:**
```json
{
  "status": "success",
  "query": "What is our company's approach to engineering effectiveness?",
  "with_rag": {
    "response": "Based on your company's documentation, your approach to engineering effectiveness focuses on four key pillars: tooling automation, developer experience, knowledge sharing, and metrics-driven improvement...",
    "sources": [
      {
        "content": "# Engineering Effectiveness Strategy\n\nOur approach focuses on four key pillars: tooling automation, developer experience, knowledge sharing, and metrics-driven improvement...",
        "metadata": {
          "source": "github.com/company/engineering-docs/strategy.md"
        }
      }
    ]
  },
  "without_rag": {
    "response": "I don't have specific information about your company's approach to engineering effectiveness. In general, engineering effectiveness often involves optimizing developer workflows, providing robust tooling, and establishing clear processes..."
  }
}
```

**Usage Example:**
```bash
curl -X POST http://localhost:8000/query-comparison \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is our company's approach to engineering effectiveness?"
  }'
```

**Common Error Codes:**
- `400 Bad Request`: Missing query parameter
- `500 Internal Server Error`: Error processing the query or connecting to the LLM

## Error Handling

All endpoints return appropriate HTTP status codes to indicate the result of the request:

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters or missing required fields
- `401 Unauthorized`: Authentication required or invalid credentials
- `404 Not Found`: Requested resource not found
- `500 Internal Server Error`: Server-side error during processing

Error responses include a detail message to help diagnose the issue:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Example error response for a missing GitHub token:
```json
{
  "detail": "GitHub token not provided. Set the GITHUB_TOKEN environment variable."
}
```

## Environment Variables

The following environment variables affect API behavior:

- `GITHUB_TOKEN`: GitHub personal access token for accessing private repositories. Required for ingesting private repositories and recommended for public repositories to avoid rate limits.
- `OLLAMA_BASE_URL`: Base URL for Ollama API (default: `http://ollama:11434`). Set this to connect to a custom Ollama instance.
- `OLLAMA_MODEL_NAME`: Name of the Ollama model to use (default: `llama2`). Change this to use a different LLM model.
- `CONFIG_PATH`: Path to the configuration file (default: `config/config.yaml`). Use this to specify a custom configuration location.
- `RAG_TEST_MODE`: Set to "true" to enable test mode, which returns simulated responses without connecting to the LLM or vector database.

## Setting Up a Cron Job for Repository Refresh

To keep your RAG system's knowledge base up-to-date with the latest content from your GitHub repositories, you can set up a cron job to periodically call the `/repos/ingest-repos` endpoint.

1. Create a script file (e.g., `refresh-repos.sh`):
```bash
#!/bin/bash
# Set your GitHub token
export GITHUB_TOKEN=your_github_token_here

# Call the API endpoint to refresh repositories
curl -X POST http://localhost:8000/repos/ingest-repos
```

2. Make the script executable:
```bash
chmod +x refresh-repos.sh
```

3. Add a cron job to run the script daily at 2 AM:
```bash
0 2 * * * /path/to/refresh-repos.sh >> /path/to/logs/github-refresh.log 2>&1
```

This setup ensures that your RAG system always has the most current information from your GitHub repositories.
