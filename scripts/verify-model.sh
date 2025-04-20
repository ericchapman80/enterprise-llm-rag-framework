
set -e

echo "=== Verifying RAG-LLM Model Configuration ==="

if ! command -v ollama &> /dev/null; then
    echo "Ollama is not installed. Please run the installation script first:"
    echo "  ./scripts/install-ollama.sh"
    exit 1
fi

if ! curl -s http://localhost:11434/api/version &> /dev/null; then
    echo "Ollama service is not running. Starting it now..."
    ollama serve &
    sleep 5
fi

echo "Available models:"
ollama list

if [ -f "config/config.yaml" ]; then
    MODEL=$(grep "model_name\|model:" config/config.yaml | grep -v "#" | head -1 | awk '{print $2}')
    echo "Current model in config: $MODEL"
    
    if [[ "$MODEL" == "llama2" ]]; then
        echo "WARNING: llama2 model requires ~8.4 GiB of memory"
        echo "Consider using a smaller model like tinyllama (~1.2 GiB) if you have memory constraints"
        echo "To switch to a smaller model, run: ./scripts/fix-memory-issue.sh"
    elif [[ "$MODEL" == "tinyllama" ]]; then
        echo "Using tinyllama model which requires ~1.2 GiB of memory"
        echo "This is suitable for systems with limited memory"
    fi
else
    echo "Config file not found at config/config.yaml"
fi

echo -e "\nSystem memory:"
free -h

echo -e "\nVerification complete. If you need to switch to a smaller model, run:"
echo "  ./scripts/fix-memory-issue.sh"
