# RAG-LLM Framework API Endpoints

This document describes the API endpoints available in the RAG-LLM Framework.

## Core Endpoints

### Health Check

```
GET /health
```

Returns the health status of the API.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### Query

```
POST /query
```

Query the RAG-LLM system with a question or prompt.

**Request Body:**
```json
{
  "query": "What is RAG?"
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

### Feedback

```
POST /feedback
```

Submit feedback for a query response.

**Request Body:**
```json
{
  "query_id": "123456",
  "feedback": "This response was very helpful and accurate."
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Feedback submitted successfully"
}
```

## Data Ingestion Endpoints

### Ingest Data

```
POST /ingest
```

Ingest data into the RAG system.

**Request Body:**
```json
{
  "source_type": "text",
  "source_data": "This is some text data to be ingested into the RAG system."
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Data ingestion started"
}
```

### Ingest GitHub Repository

```
POST /ingest/github
```

Ingest a GitHub repository into the RAG system. This endpoint will clone the repository and process all files matching the specified file extensions.

**Request Body:**
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

**Note:** This endpoint requires the `GITHUB_TOKEN` environment variable to be set for accessing private repositories.

## Data Management Endpoints

### List Ingested Data Sources

```
GET /ingested
```

List all ingested data sources and document counts.

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

### View Ingested Data

```
GET /ingested-data
```

View all ingested documents with their content and metadata.

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

### Flush Database

```
POST /flush-database
```

Flush all documents from the vector database.

**Response:**
```json
{
  "status": "success",
  "message": "Vector database flushed successfully"
}
```

## Demonstration Endpoints

### Query Comparison

```
POST /query-comparison
```

Compare responses with and without RAG context. This endpoint is useful for demonstrating the power of RAG by showing how the model's responses differ when it has access to your specific knowledge base.

**Request Body:**
```json
{
  "query": "What is our company's approach to engineering effectiveness?"
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

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters
- `500 Internal Server Error`: Server-side error

Error responses include a detail message:

```json
{
  "detail": "Error message describing what went wrong"
}
```

## Environment Variables

The following environment variables affect API behavior:

- `GITHUB_TOKEN`: GitHub personal access token for accessing private repositories
- `OLLAMA_BASE_URL`: Base URL for Ollama API (default: `http://ollama:11434`)
- `OLLAMA_MODEL_NAME`: Name of the Ollama model to use (default: `llama2`)
