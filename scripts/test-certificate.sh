set -e

echo "=== Testing Zscaler Certificate Installation ==="
echo "This script will test if the Zscaler certificate is properly installed in the Ollama container."

CONTAINER_ID=$(docker ps | grep ollama | awk '{print $1}')

if [ -z "$CONTAINER_ID" ]; then
  echo "Error: Ollama container not found. Make sure it's running."
  exit 1
fi

echo "Found Ollama container: $CONTAINER_ID"

echo "Testing certificate by pulling llama2 model..."
docker exec $CONTAINER_ID ollama pull llama2:latest

echo "If no certificate errors appeared, the certificate is properly installed!"
echo "You can now use the RAG-LLM framework with the Ollama model."
