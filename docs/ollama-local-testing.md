# Testing RAG-LLM Framework with Ollama Locally

This guide provides detailed instructions for testing the RAG-LLM Framework with Ollama on your local machine.

## Prerequisites

1. Ensure you have Python 3.8+ installed
2. Download and install Ollama from [https://ollama.com/download](https://ollama.com/download)
3. Extract the RAG-LLM Framework package to your local machine

## Step 1: Install Ollama

Follow the installation instructions for your operating system:

### macOS
```bash
brew install ollama
```

### Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Windows
Download the installer from [https://ollama.com/download](https://ollama.com/download)

## Step 2: Pull a Model

For testing purposes, we recommend starting with a smaller model:

```bash
ollama pull tinyllama
```

Other options include:
- `ollama pull llama2` (larger, better quality)
- `ollama pull mistral` (good balance of size and quality)

## Step 3: Configure the Framework

1. Create a configuration file:

```bash
mkdir -p config
cat > config/config.yaml << 'EOL'
llm:
  provider: "ollama"
  model: "tinyllama"  # Use the model you pulled
  temperature: 0.7
  max_tokens: 2048

vector_db:
  provider: "chroma"
  path: "./data/chroma_db"

embeddings:
  model: "all-MiniLM-L6-v2"
EOL
```

2. Create a `.env` file:

```bash
cp .env.example .env
```

Edit the `.env` file to add your GitHub token if you want to test GitHub repository ingestion.

## Step 4: Start Ollama Server

```bash
ollama serve
```

This will start the Ollama server in the foreground. Keep this terminal window open.

## Step 5: Start the Backend

In a new terminal:

```bash
# Create a Python virtual environment
python -m venv rag-llm-env

# Activate the virtual environment
source rag-llm-env/bin/activate  # On Windows: rag-llm-env\Scripts\activate

# Install dependencies
pip install -r src/backend/requirements.txt

# Start the backend
./scripts/run-local-native.sh
```

This script sets up the necessary environment and starts the FastAPI server with Ollama integration.

## Step 6: Start the Web UI

In another terminal:

```bash
./scripts/run-web-ui.sh
```

## Step 7: Access the Web UI

Open your browser and navigate to:

```
http://127.0.0.1:8080
```

Note: These instructions are for running the application on your local machine after downloading and extracting the package.

## Step 8: Test the Chat Functionality

1. Type a message in the chat input
2. The message will be sent to the backend
3. The backend will use Ollama to generate a response
4. The response will be displayed in the chat UI

## Troubleshooting

### Ollama Connection Issues

If the backend cannot connect to Ollama, check:

1. Ensure Ollama is running (`ollama serve`)
2. Verify the model is downloaded (`ollama list`)
3. Check the backend logs for specific errors

### Memory Issues

If you encounter memory errors with larger models:

1. Try using a smaller model like `tinyllama`
2. Adjust the `max_tokens` parameter in `config/config.yaml`
3. Run the memory fix script: `./scripts/fix-memory-issue.sh`

### API Errors

If you see API errors in the web UI:

1. Check that the backend is running on port 8000
2. Verify CORS is properly configured
3. Check the browser console for specific error messages

## Advanced Testing

### Testing GitHub Repository Ingestion

1. Ensure your GitHub token is set in the `.env` file
2. Use the API endpoint: `POST http://localhost:8000/ingest/github`
3. Provide a repository URL in the request body

### Testing with Different Models

1. Pull a different model: `ollama pull modelname`
2. Update the model name in `config/config.yaml`
3. Restart the backend

## Monitoring

### Backend Logs

The backend logs will show:
- API requests
- Ollama interactions
- Error messages

### Ollama Logs

The Ollama server logs will show:
- Model loading
- Inference requests
- Memory usage
