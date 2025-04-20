# Native Local Setup Guide (No Containers)

This guide explains how to run the RAG-LLM framework directly on your local machine without any containers or Kubernetes. This approach gives you maximum flexibility and direct access to all components.

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Node.js 16+ (for Backstage plugin)
- npm or yarn (for Backstage plugin)

## Step 1: Install Ollama

Ollama is a lightweight LLM server that runs locally on your machine.

### For macOS:

```bash
brew install ollama
```

### For Linux:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### For Windows:

Download the installer from [Ollama's website](https://ollama.com/download).

## Step 2: Pull the LLM Model

```bash
# Start Ollama service
ollama serve &

# Pull the model
ollama pull llama2
```

## Step 3: Set Up Python Environment

It's recommended to use a virtual environment to avoid conflicts with other Python packages:

```bash
# Create a virtual environment
python -m venv rag-llm-env

# Activate the virtual environment
# On Linux/macOS:
source rag-llm-env/bin/activate
# On Windows:
.\rag-llm-env\Scripts\activate

# Install backend dependencies
pip install -r src/backend/requirements.txt

# Install Slack bot dependencies (if needed)
pip install -r src/integrations/slack/requirements.txt
```

## Step 4: Set Up Environment Variables

Create a `.env` file in the root directory:

```bash
# Copy the example .env file
cp .env.example .env

# Edit the .env file with your credentials
```

Then load the environment variables:

```bash
# On Linux/macOS:
export $(grep -v '^#' .env | xargs)

# On Windows PowerShell:
# Get-Content .env | ForEach-Object { if ($_ -match '^\s*([^#].+?)=(.*)$') { [Environment]::SetEnvironmentVariable($matches[1], $matches[2]) } }
```

## Step 5: Run the Backend Service

```bash
# Set PYTHONPATH to include the project root
export PYTHONPATH=$PWD

# Run the FastAPI server
cd src/backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The backend will be available at:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs

## Step 6: Run the Slack Bot (Optional)

Open a new terminal window, activate the virtual environment, and run:

```bash
# Activate the virtual environment
source rag-llm-env/bin/activate

# Set PYTHONPATH
export PYTHONPATH=$PWD

# Run the Slack bot
cd src/integrations/slack
python slack_bot.py
```

## Step 7: Install Backstage Plugin (Optional)

If you have an existing Backstage instance:

```bash
# Navigate to your Backstage app
cd path/to/your/backstage/app

# Copy the plugin
cp -r /path/to/rag-llm-framework/src/integrations/backstage/backstage-plugin ./plugins/rag-llm

# Install dependencies
yarn install

# Start Backstage
yarn start
```

## Convenience Scripts

For easier startup, you can use the provided convenience scripts:

```bash
# Make scripts executable
chmod +x scripts/run-local-native.sh
chmod +x scripts/run-slackbot-native.sh

# Run the backend
./scripts/run-local-native.sh

# In another terminal, run the Slack bot
./scripts/run-slackbot-native.sh
```

## Data Persistence

When running natively:

- Vector database will be stored in `./data/chroma_db` by default
- Ollama models will be stored in Ollama's default location (`~/.ollama`)

## Troubleshooting

### Import Errors

If you encounter import errors:

1. Make sure PYTHONPATH is set correctly:
   ```bash
   export PYTHONPATH=/full/path/to/rag-llm-framework
   ```

2. Check that __init__.py files exist in:
   - src/
   - src/backend/

### Ollama Connection Issues

If the backend can't connect to Ollama:

1. Ensure Ollama is running:
   ```bash
   ollama serve
   ```

2. Verify the model is downloaded:
   ```bash
   ollama list
   ```

3. Check the OLLAMA_BASE_URL in your environment:
   ```bash
   echo $OLLAMA_BASE_URL
   ```
   It should be set to `http://localhost:11434` for local development.
