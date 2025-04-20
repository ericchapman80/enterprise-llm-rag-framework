# 
# 
# 
# 
# 

set -e

PORT=8000

while [[ $# -gt 0 ]]; do
  case $1 in
    --port)
      PORT="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

echo "=== Starting RAG-LLM Backend in Test Mode ==="
echo "Note: This mode bypasses Ollama requirements for testing purposes."
echo "      Responses will be mock data and not use a real LLM."

if [ ! -d "rag-llm-env" ]; then
    echo "Creating Python virtual environment..."
    python -m venv rag-llm-env
fi

echo "Activating virtual environment..."
source rag-llm-env/bin/activate

echo "Installing backend dependencies..."
pip install -r src/backend/requirements.txt

echo "Ensuring python-multipart is installed..."
pip install python-multipart

if [ ! -f ".env" ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "Please edit .env file with your credentials"
fi

echo "Loading environment variables..."
export $(grep -v '^#' .env | xargs)

mkdir -p data/chroma_db
mkdir -p src
mkdir -p src/backend
mkdir -p config

touch src/__init__.py
touch src/backend/__init__.py

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

export PYTHONPATH=$PWD
export RAG_TEST_MODE=true

CONFIG_DIR="$PWD/config"
if [ ! -d "$CONFIG_DIR" ]; then
    mkdir -p "$CONFIG_DIR"
fi

echo "Starting FastAPI server in test mode on port $PORT..."
cd src/backend
ln -sf ../../config .
uvicorn main:app --host 0.0.0.0 --port $PORT --reload
