set -e


if ! command -v brew &> /dev/null; then
    echo "Homebrew is not installed. Please install it first."
    echo "Visit https://brew.sh for installation instructions."
    exit 1
fi

echo "Installing dependencies from Brewfile..."
brew bundle

if ! command -v rdctl &> /dev/null; then
    echo "Rancher Desktop is not installed. Please install it first."
    echo "Visit https://rancherdesktop.io for installation instructions."
    exit 1
fi

echo "Checking Rancher Desktop status..."
if ! rdctl list 2>/dev/null | grep -q "running"; then
    echo "Starting Rancher Desktop..."
    rdctl start
    echo "Waiting for Rancher Desktop to start..."
    sleep 30
fi

echo "Pulling Ollama model (llama2)..."
ollama pull llama2

if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL_NAME=llama2

GITHUB_TOKEN=your_github_token

SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
SLACK_SIGNING_SECRET=your-signing-secret

API_HOST=0.0.0.0
API_PORT=8000
EOF
    echo "Please update the .env file with your actual tokens and secrets."
fi

mkdir -p data/chroma_db

echo "Starting services with Docker Compose..."
docker-compose up -d

echo "Setup complete! The RAG-enabled LLM framework is now running."
echo "- Backend API: http://localhost:8000"
echo "- Ollama: http://localhost:11434"
echo ""
echo "To stop the services, run: docker-compose down"
