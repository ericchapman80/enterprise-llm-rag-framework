set -e

NAMESPACE=${1:-rag-llm}
KUBE_CONTEXT=$(kubectl config current-context)

echo "=== Testing Zscaler Certificate Installation in Kubernetes ==="
echo "This script will test if the Zscaler certificate is properly installed in the Ollama pod."

OLLAMA_POD=$(kubectl --context $KUBE_CONTEXT get pod -n $NAMESPACE -l app=ollama -o jsonpath='{.items[0].metadata.name}')

if [ -z "$OLLAMA_POD" ]; then
  echo "Error: Ollama pod not found in namespace $NAMESPACE. Make sure it's running."
  exit 1
fi

echo "Found Ollama pod: $OLLAMA_POD"

echo "Testing certificate by pulling llama2 model..."
kubectl --context $KUBE_CONTEXT exec -n $NAMESPACE $OLLAMA_POD -- ollama pull llama2:latest

echo "If no certificate errors appeared, the certificate is properly installed!"
echo "You can now use the RAG-LLM framework with the Ollama model in Kubernetes."
