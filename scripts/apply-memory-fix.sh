
set -e

echo "=== Applying Memory Fix for RAG-LLM Framework ==="

if [ ! -f "memory-fix.patch" ]; then
    echo "Error: memory-fix.patch file not found"
    exit 1
fi

echo "Applying patch to run-local-native.sh..."
patch -p0 < memory-fix.patch

chmod +x scripts/run-local-native-small-model.sh

echo "Updating config.yaml to use tinyllama model..."
sed -i 's/model_name: llama2/model_name: tinyllama/g' config/config.yaml

if [ ! -f ".env" ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
fi

echo "Updating .env file to use tinyllama model..."
if grep -q "OLLAMA_MODEL_NAME" .env; then
    sed -i 's/OLLAMA_MODEL_NAME=.*/OLLAMA_MODEL_NAME=tinyllama/g' .env
else
    echo "OLLAMA_MODEL_NAME=tinyllama" >> .env
fi

if command -v ollama &> /dev/null; then
    echo "Pulling tinyllama model (this may take a while)..."
    ollama pull tinyllama
else
    echo "Ollama not found. Please install ollama and run 'ollama pull tinyllama' manually."
fi

echo "Memory fix applied successfully!"
echo "You can now run the application with the smaller model using:"
echo "  ./scripts/run-local-native-small-model.sh"
echo ""
echo "Or run your original script which now uses tinyllama:"
echo "  ./scripts/run-local-native.sh"
