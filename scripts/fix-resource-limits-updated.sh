
set -e

NAMESPACE="rag-llm"
KUBE_CONTEXT=$(kubectl config current-context)

echo "=== Updating Helm deployment with reduced resource requirements ==="
helm upgrade --install rag-llm-framework ./helm/rag-llm-framework \
  --kube-context $KUBE_CONTEXT \
  --namespace $NAMESPACE \
  --set backend.resources.requests.cpu=100m \
  --set backend.resources.requests.memory=256Mi \
  --set backend.resources.limits.cpu=500m \
  --set backend.resources.limits.memory=512Mi \
  --set ollama.resources.requests.cpu=100m \
  --set ollama.resources.requests.memory=256Mi \
  --set ollama.resources.limits.cpu=500m \
  --set ollama.resources.limits.memory=1Gi \
  --set slackbot.resources.requests.cpu=50m \
  --set slackbot.resources.requests.memory=128Mi \
  --set slackbot.resources.limits.cpu=200m \
  --set slackbot.resources.limits.memory=256Mi

echo "=== Checking pod status after update ==="
kubectl --context $KUBE_CONTEXT get pods -n $NAMESPACE

echo "=== Waiting for backend pod to start (this may take a minute) ==="
kubectl --context $KUBE_CONTEXT wait --for=condition=Ready pod -l app=rag-llm-backend -n $NAMESPACE --timeout=120s || true

echo "=== Checking backend pod status ==="
kubectl --context $KUBE_CONTEXT get pods -n $NAMESPACE -l app=rag-llm-backend

echo "=== If the pod is running, test the health endpoint ==="
echo "curl http://rag-llm.local/health"
