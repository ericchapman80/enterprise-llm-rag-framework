
set -e

echo "=== Fixing Memory Issue for RAG-LLM Framework (macOS Compatible) ==="

echo "Updating config.yaml to use tinyllama model..."
sed -i '' 's/model_name: llama2/model_name: tinyllama/g' config/config.yaml

if [ ! -f ".env" ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
fi

echo "Updating .env file to use tinyllama model..."
if grep -q "OLLAMA_MODEL_NAME" .env; then
    sed -i '' 's/OLLAMA_MODEL_NAME=.*/OLLAMA_MODEL_NAME=tinyllama/g' .env
else
    echo "OLLAMA_MODEL_NAME=tinyllama" >> .env
fi

if command -v ollama &> /dev/null; then
    echo "Pulling tinyllama model (this may take a while)..."
    ollama pull tinyllama
else
    echo "Ollama not found. Please install ollama and run 'ollama pull tinyllama' manually."
fi

echo "Updating run-local-native.sh to use tinyllama model..."
sed -i '' 's/if ! ollama list | grep -q "llama2"; then/if ! ollama list | grep -q "tinyllama"; then/g' scripts/run-local-native.sh
sed -i '' 's/echo "Pulling llama2 model (this may take a while)..."/echo "Pulling tinyllama model (this may take a while)..."/g' scripts/run-local-native.sh
sed -i '' 's/ollama pull llama2/ollama pull tinyllama/g' scripts/run-local-native.sh
sed -i '' 's/model: "llama2"/model: "tinyllama"/g' scripts/run-local-native.sh

echo "Memory fix applied successfully!"
echo "You can now run the application with the smaller model using:"
echo "  ./scripts/run-local-native.sh"
