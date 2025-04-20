
set -e

NAMESPACE=${1:-rag-llm}
BACKEND_POD=$(kubectl get pod -n $NAMESPACE -l app=rag-llm-backend -o jsonpath='{.items[0].metadata.name}')

if [ -z "$BACKEND_POD" ]; then
  echo "Error: Backend pod not found in namespace $NAMESPACE"
  exit 1
fi

echo "=== Testing import paths in pod $BACKEND_POD ==="

echo "1. Checking PYTHONPATH environment variable:"
kubectl exec -n $NAMESPACE $BACKEND_POD -- env | grep PYTHONPATH

echo "2. Checking Python sys.path:"
kubectl exec -n $NAMESPACE $BACKEND_POD -- python3 -c "import sys; print(sys.path)"

echo "3. Testing direct import:"
kubectl exec -n $NAMESPACE $BACKEND_POD -- python3 -c "
try:
    from rag_engine import RAGEngine
    print('✅ Direct import works')
except ImportError as e:
    print('❌ Direct import failed:', e)
"

echo "4. Testing absolute import from src.backend:"
kubectl exec -n $NAMESPACE $BACKEND_POD -- python3 -c "
try:
    from src.backend.rag_engine import RAGEngine
    print('✅ Absolute import from src.backend works')
except ImportError as e:
    print('❌ Absolute import from src.backend failed:', e)
"

echo "5. Testing absolute import from backend:"
kubectl exec -n $NAMESPACE $BACKEND_POD -- python3 -c "
try:
    from backend.rag_engine import RAGEngine
    print('✅ Absolute import from backend works')
except ImportError as e:
    print('❌ Absolute import from backend failed:', e)
"

echo "6. Testing with sys.path modification:"
kubectl exec -n $NAMESPACE $BACKEND_POD -- python3 -c "
import sys
sys.path.append('/app')
sys.path.append('/app/src')
sys.path.append('/app/src/backend')
print('Updated sys.path:', sys.path)

try:
    from rag_engine import RAGEngine
    print('✅ Import after sys.path modification works')
except ImportError as e:
    print('❌ Import after sys.path modification failed:', e)
"

echo "7. Checking file structure:"
kubectl exec -n $NAMESPACE $BACKEND_POD -- ls -la /app
kubectl exec -n $NAMESPACE $BACKEND_POD -- ls -la /app/src
kubectl exec -n $NAMESPACE $BACKEND_POD -- ls -la /app/src/backend

echo "=== Import path testing complete ==="
