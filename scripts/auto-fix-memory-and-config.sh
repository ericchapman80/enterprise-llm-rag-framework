# 
# 
# 
# 

set -e

echo "=== RAG-LLM Framework Auto-Fix Script ==="
echo "Detecting system memory and fixing configuration paths..."

if [[ "$OSTYPE" == "darwin"* ]]; then
    AVAILABLE_MEM=$(sysctl hw.memsize | awk '{print $2 / 1024 / 1024 / 1024}')
else
    AVAILABLE_MEM=$(free -g | grep Mem | awk '{print $7}')
fi

echo "Available memory: ${AVAILABLE_MEM}GB"

mkdir -p config

if [ ! -f "config/config.yaml" ]; then
    echo "Creating default config file..."
    cat > config/config.yaml << EOF
llm:
  provider: "ollama"
  model: "tinyllama"
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

if [ -f "src/backend/main.py" ]; then
    echo "Fixing config path in main.py..."
    sed -i.bak 's|/app/config/config.yaml|./config/config.yaml|g' src/backend/main.py
    sed -i.bak 's|os.path.join(os.path.dirname(__file__), "..", "..", "config", "config.yaml")|os.path.join(os.getcwd(), "config", "config.yaml")|g' src/backend/main.py
    echo "Config path fixed in main.py"
fi

if (( $(echo "$AVAILABLE_MEM < 6" | bc -l) )); then
    echo "Limited memory detected (${AVAILABLE_MEM}GB). Switching to tinyllama model..."
    
    sed -i.bak 's/model: "llama2"/model: "tinyllama"/g' config/config.yaml
    
    if [ -f "helm/rag-llm-framework/values.yaml" ]; then
        sed -i.bak 's/model_name: llama2/model_name: tinyllama/g' helm/rag-llm-framework/values.yaml
    fi
    
    echo "Model switched to tinyllama in configuration files"
    
    if command -v ollama &> /dev/null; then
        echo "Pulling tinyllama model (this may take a while)..."
        ollama pull tinyllama
    else
        echo "Ollama not found. Please install Ollama and run 'ollama pull tinyllama'"
    fi
else
    echo "Sufficient memory available (${AVAILABLE_MEM}GB). No model change needed."
fi

echo "Creating symbolic links for config in common locations..."
mkdir -p /tmp/app/config
ln -sf "$(pwd)/config/config.yaml" /tmp/app/config/config.yaml

echo "=== Auto-fix complete ==="
echo "You can now run the application with:"
echo "  ./scripts/run-local-native.sh"
echo "Or for Kubernetes deployment:"
echo "  make deploy"
