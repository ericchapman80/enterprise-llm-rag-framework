set -e

NAMESPACE=${1:-rag-llm}
MODEL=${2:-llama2}
KUBE_CONTEXT=$(kubectl config current-context)

echo "Pulling Ollama model $MODEL in namespace $NAMESPACE using context $KUBE_CONTEXT..."

OLLAMA_POD=$(kubectl --context $KUBE_CONTEXT get pod -l app=ollama -n $NAMESPACE -o jsonpath="{.items[0].metadata.name}")
if [ -z "$OLLAMA_POD" ]; then
    echo "Error: No Ollama pod found in namespace $NAMESPACE"
    exit 1
fi

kubectl --context $KUBE_CONTEXT exec -it $OLLAMA_POD -n $NAMESPACE -- ollama pull $MODEL

echo "Model $MODEL successfully pulled."
