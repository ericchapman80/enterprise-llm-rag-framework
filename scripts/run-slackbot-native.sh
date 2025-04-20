
set -e

echo "=== Starting RAG-LLM Slack Bot Natively ==="

if [ ! -d "rag-llm-env" ]; then
    echo "Creating Python virtual environment..."
    python -m venv rag-llm-env
fi

echo "Activating virtual environment..."
source rag-llm-env/bin/activate

echo "Installing Slack bot dependencies..."
pip install -r src/integrations/slack/requirements.txt

echo "Ensuring python-multipart is installed..."
pip install python-multipart

if [ ! -f ".env" ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "Please edit .env file with your Slack credentials"
    echo "You need to set SLACK_BOT_TOKEN, SLACK_APP_TOKEN, and SLACK_SIGNING_SECRET"
    exit 1
fi

echo "Loading environment variables..."
export $(grep -v '^#' .env | xargs)

if [ -z "$SLACK_BOT_TOKEN" ] || [ -z "$SLACK_APP_TOKEN" ] || [ -z "$SLACK_SIGNING_SECRET" ]; then
    echo "Error: Slack credentials not found in .env file"
    echo "Please set SLACK_BOT_TOKEN, SLACK_APP_TOKEN, and SLACK_SIGNING_SECRET"
    exit 1
fi

mkdir -p src
mkdir -p src/integrations
mkdir -p src/integrations/slack
mkdir -p config

touch src/__init__.py
touch src/integrations/__init__.py
touch src/integrations/slack/__init__.py

if [ ! -f "config/config.yaml" ]; then
    echo "Creating default config file..."
    cat > config/config.yaml << EOF
llm:
  provider: "ollama"
  model: "llama2"
  temperature: 0.7
  max_tokens: 2048

vector_db:
  provider: "chroma"
  path: "./data/chroma_db"

embeddings:
  model: "all-MiniLM-L6-v2"
EOF
    echo "Default config file created at config/config.yaml"
fi

export PYTHONPATH=$PWD

export RAG_API_URL="http://localhost:8000"

echo "Starting Slack bot..."
cd src/integrations/slack
python slack_bot.py
