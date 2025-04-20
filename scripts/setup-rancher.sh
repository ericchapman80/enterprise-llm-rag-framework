set -e

NAMESPACE="rag-llm"
ENV_FILE=".env"
USE_ENV_FILE=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --namespace)
      NAMESPACE="$2"
      shift 2
      ;;
    --env-file)
      ENV_FILE="$2"
      USE_ENV_FILE=true
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

if ! command -v rdctl &> /dev/null; then
    echo "Rancher Desktop is not installed. Please install it first."
    exit 1
fi

RANCHER_STATUS=$(rdctl list 2>/dev/null || echo "error")
if [[ "$RANCHER_STATUS" == "error" || ! "$RANCHER_STATUS" =~ "running" ]]; then
    echo "Starting Rancher Desktop..."
    rdctl start --interactive=false
    echo "Waiting for Rancher Desktop to start..."
    sleep 30
else
    echo "Rancher Desktop is already running."
fi

if ! command -v kubectl &> /dev/null; then
    echo "kubectl is not installed. Installing via Homebrew..."
    brew install kubernetes-cli
fi

if ! command -v helm &> /dev/null; then
    echo "Helm is not installed. Installing via Homebrew..."
    brew install helm
fi

if [ -f "Brewfile" ]; then
    echo "Installing dependencies from Brewfile..."
    brew bundle
fi

if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
    echo "Creating namespace $NAMESPACE..."
    kubectl create namespace "$NAMESPACE"
fi

echo "Building Docker images..."
docker build -t rag-llm-backend:latest .
docker build -t rag-llm-slackbot:latest -f Dockerfile.slack .

if [ "$USE_ENV_FILE" = true ]; then
    if [ -f "$ENV_FILE" ]; then
        echo "Loading secrets from $ENV_FILE..."
        chmod +x scripts/load-env-to-k8s.sh
        ./scripts/load-env-to-k8s.sh --namespace "$NAMESPACE" --env-file "$ENV_FILE"
        
        HELM_SECRET_ARGS="--set secrets.create=false --set secrets.existingSecret=$NAMESPACE-secrets"
    else
        echo "Warning: .env file not found at $ENV_FILE. Proceeding without secrets."
        HELM_SECRET_ARGS=""
    fi
else
    HELM_SECRET_ARGS=""
fi

echo "Installing/upgrading Helm chart..."
helm upgrade --install rag-llm-framework ./helm/rag-llm-framework \
    --namespace "$NAMESPACE" \
    --set global.environment=development \
    --set backend.ingress.hosts[0].host=rag-llm.local \
    $HELM_SECRET_ARGS

if ! grep -q "rag-llm.local" /etc/hosts; then
    echo "Adding rag-llm.local to /etc/hosts..."
    echo "127.0.0.1 rag-llm.local" | sudo tee -a /etc/hosts
fi

echo "Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app=rag-llm-backend --timeout=300s --namespace "$NAMESPACE"
kubectl wait --for=condition=ready pod -l app=ollama --timeout=300s --namespace "$NAMESPACE"

echo "Pulling Ollama model (this may take a while)..."
kubectl exec -it $(kubectl get pod -l app=ollama -n "$NAMESPACE" -o jsonpath="{.items[0].metadata.name}") -n "$NAMESPACE" -- ollama pull llama2

echo "Setup complete! You can access the RAG-LLM Framework at http://rag-llm.local"
echo "To configure Slack integration, update the secrets in the Helm chart values or create a Kubernetes secret."
