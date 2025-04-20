
set -e

echo "=== Installing Ollama for RAG-LLM Framework ==="

if [[ "$OSTYPE" == "darwin"* ]]; then
    if command -v brew &> /dev/null; then
        echo "Installing Ollama using Homebrew..."
        brew install ollama
    else
        echo "Homebrew not found. Please install Homebrew first:"
        echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Installing Ollama on Linux..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "For Windows, please download Ollama from https://ollama.com/download"
    echo "After installation, restart your terminal and run the RAG-LLM scripts again."
    exit 1
fi

echo "Starting Ollama service..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    ollama serve &
    sleep 2
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    systemctl --user start ollama || ollama serve &
    sleep 2
fi

echo "Pulling tinyllama model (this may take a while)..."
ollama pull tinyllama

echo "Ollama installation complete!"
echo "You can now run the RAG-LLM Framework with:"
echo "  ./scripts/run-local-native-small-model.sh"
