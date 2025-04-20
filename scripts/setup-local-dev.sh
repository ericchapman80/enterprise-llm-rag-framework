
set -e

echo "=== Setting up RAG-LLM Framework for local development ==="

if [ ! -f ".env" ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "Please edit .env file with your credentials"
fi

if ! command -v ollama &> /dev/null; then
    echo "Ollama is not installed. Please install it first:"
    echo "  - macOS: brew install ollama"
    echo "  - Linux: curl -fsSL https://ollama.com/install.sh | sh"
    echo "  - Windows: Download from https://ollama.com/download"
    exit 1
fi

if ! curl -s http://localhost:11434/api/version &> /dev/null; then
    echo "Starting Ollama service..."
    ollama serve &
    sleep 5
fi

if ! ollama list | grep -q "llama2"; then
    echo "Pulling llama2 model (this may take a while)..."
    ollama pull llama2
fi

echo "Building and starting services with Docker Compose..."
docker-compose build
docker-compose up -d

echo "=== Setup complete! ==="
echo "The RAG-LLM Framework is now running:"
echo "  - Backend API: http://localhost:8000"
echo "  - API Documentation: http://localhost:8000/docs"
echo "  - Ollama: http://localhost:11434"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop all services:"
echo "  docker-compose down"
echo ""
echo "For more information, see docs/local-setup.md"
