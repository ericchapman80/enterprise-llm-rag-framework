set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

TEST_MODULES="core,chat,repo"
REPORT_FORMAT="html,json"
TEST_PORT=8000
LOG_DIR="test-logs"

mkdir -p "${LOG_DIR}"

echo -e "${GREEN}=== Enterprise LLM RAG Framework Testing Suite ===${NC}"
echo "This script will test the framework in three deployment modes:"
echo "1. Local Python"
echo "2. Docker Compose"
echo "3. Kubernetes (via Helm)"

function cleanup {
  echo -e "${YELLOW}Performing cleanup...${NC}"
  
  pkill -f "uvicorn src.backend.main:app" || true
  
  if [ -f "docker-compose.yml" ]; then
    docker-compose down || true
  fi
  
  if command -v helm &> /dev/null && kubectl get namespace rag-llm &> /dev/null; then
    helm uninstall rag-llm -n rag-llm || true
  fi
  
  echo -e "${GREEN}Cleanup complete.${NC}"
}

trap cleanup EXIT

function run_tests {
  local mode=$1
  local url=$2
  
  echo -e "${GREEN}Running tests for ${mode} mode...${NC}"
  export RAG_API_URL="${url}"
  export RAG_TEST_MODE="true"
  
  echo "Verifying deployment..."
  python tests/post_deployment/verify_deployment.py --url "${RAG_API_URL}" --retries 5 --delay 2
  if [ $? -ne 0 ]; then
    echo -e "${RED}Deployment verification failed for ${mode} mode.${NC}"
    return 1
  fi
  
  echo "Running post-deployment tests..."
  python tests/post_deployment/run_tests.py --modules "${TEST_MODULES}" --report "${REPORT_FORMAT}" --output-dir "${LOG_DIR}/${mode}"
  local test_status=$?
  
  if [ $test_status -eq 0 ]; then
    echo -e "${GREEN}All tests passed for ${mode} mode!${NC}"
  else
    echo -e "${RED}Tests failed for ${mode} mode. See logs for details.${NC}"
  fi
  
  return $test_status
}

function test_local_python {
  echo -e "${GREEN}=== Testing Mode 1: Local Python ===${NC}"
  echo "Starting local Python deployment..."
  
  ./scripts/deploy-and-test.sh --port ${TEST_PORT} --modules "${TEST_MODULES}" --report "${REPORT_FORMAT}"
  local status=$?
  
  if [ $status -eq 0 ]; then
    echo -e "${GREEN}Local Python mode tests passed!${NC}"
  else
    echo -e "${RED}Local Python mode tests failed.${NC}"
  fi
  
  return $status
}

function test_docker_compose {
  echo -e "${GREEN}=== Testing Mode 2: Docker Compose ===${NC}"
  
  if ! command -v docker &> /dev/null || ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker or Docker Compose not installed. Skipping Docker Compose tests.${NC}"
    return 1
  fi
  
  echo "Running Docker Compose test script..."
  ./scripts/test-docker-compose.sh
  local status=$?
  
  if [ $status -eq 0 ]; then
    echo -e "${GREEN}Docker Compose test script completed successfully.${NC}"
    
    echo "Running post-deployment tests against Docker Compose..."
    run_tests "docker-compose" "http://localhost:${TEST_PORT}"
    status=$?
  else
    echo -e "${RED}Docker Compose test script failed. Skipping post-deployment tests.${NC}"
  fi
  
  return $status
}

function test_kubernetes {
  echo -e "${GREEN}=== Testing Mode 3: Kubernetes (Helm) ===${NC}"
  
  if ! command -v kubectl &> /dev/null || ! command -v helm &> /dev/null; then
    echo -e "${RED}Kubernetes CLI (kubectl) or Helm not installed. Skipping Kubernetes tests.${NC}"
    return 1
  fi
  
  if ! kubectl get nodes &> /dev/null; then
    echo -e "${RED}Kubernetes cluster not accessible. Skipping Kubernetes tests.${NC}"
    return 1
  fi
  
  kubectl create namespace rag-llm --dry-run=client -o yaml | kubectl apply -f -
  
  echo "Deploying application with Helm..."
  helm upgrade --install rag-llm ./helm/rag-llm-framework --namespace rag-llm -f ./helm/rag-llm-framework/values-test.yaml
  
  echo "Waiting for deployment to complete..."
  kubectl rollout status deployment -n rag-llm rag-llm-backend
  
  local service_url
  if kubectl get svc -n rag-llm rag-llm-backend -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null; then
    service_ip=$(kubectl get svc -n rag-llm rag-llm-backend -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    service_port=$(kubectl get svc -n rag-llm rag-llm-backend -o jsonpath='{.spec.ports[0].port}')
    service_url="http://${service_ip}:${service_port}"
  else
    echo "No LoadBalancer found, using port-forward..."
    kubectl port-forward -n rag-llm svc/rag-llm-backend ${TEST_PORT}:8000 &
    port_forward_pid=$!
    service_url="http://localhost:${TEST_PORT}"
    sleep 5
  fi
  
  run_tests "kubernetes" "${service_url}"
  local status=$?
  
  if [ -n "${port_forward_pid}" ]; then
    kill ${port_forward_pid} || true
  fi
  
  echo "Uninstalling Helm chart..."
  helm uninstall rag-llm -n rag-llm
  
  return $status
}

python_status=0
docker_status=0
k8s_status=0

test_local_python
python_status=$?

test_docker_compose
docker_status=$?

test_kubernetes
k8s_status=$?

echo -e "${GREEN}=== Test Summary ===${NC}"
echo -e "Local Python: $([ $python_status -eq 0 ] && echo "${GREEN}PASSED${NC}" || echo "${RED}FAILED${NC}")"
echo -e "Docker Compose: $([ $docker_status -eq 0 ] && echo "${GREEN}PASSED${NC}" || echo "${RED}FAILED${NC}")"
echo -e "Kubernetes: $([ $k8s_status -eq 0 ] && echo "${GREEN}PASSED${NC}" || echo "${RED}FAILED${NC}")"

if [ $python_status -eq 0 ] && [ $docker_status -eq 0 ] && [ $k8s_status -eq 0 ]; then
  echo -e "${GREEN}All deployment modes tested successfully!${NC}"
  exit 0
else
  echo -e "${RED}Some tests failed. See logs for details.${NC}"
  exit 1
fi
