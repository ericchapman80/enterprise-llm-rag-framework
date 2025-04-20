
set -e

echo "=== Fixing import error in main.py ==="

cp src/backend/main.py src/backend/main.py.bak

cp src/backend/main.py.fixed src/backend/main.py

echo "=== Updated main.py with robust import handling ==="
echo "The new main.py will try multiple import approaches:"
echo "1. from src.backend.rag_engine import RAGEngine"
echo "2. from backend.rag_engine import RAGEngine"
echo "3. from .rag_engine import RAGEngine"
echo "4. Direct import with sys.path modification"

echo "=== Rebuilding Docker image ==="
docker build -t rag-llm-backend:latest .

echo "=== Redeploying to Kubernetes ==="
helm upgrade --install rag-llm-framework ./helm/rag-llm-framework \
  --namespace rag-llm \
  --set backend.resources.requests.cpu=100m \
  --set backend.resources.limits.cpu=500m

echo "=== Waiting for backend pod to restart ==="
kubectl -n rag-llm rollout restart deployment rag-llm-backend
kubectl -n rag-llm rollout status deployment rag-llm-backend

echo "=== Checking backend pod status ==="
kubectl -n rag-llm get pods -l app=rag-llm-backend

echo "=== Import error fix complete ==="
echo "To verify the fix, check the backend pod logs:"
echo "kubectl -n rag-llm logs -l app=rag-llm-backend"
