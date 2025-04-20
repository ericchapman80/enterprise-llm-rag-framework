set -e

export RAG_TEST_MODE="true"  # Run in test mode
API_PORT=8000
TEST_MODULES="core,chat,repo"
PARALLEL=true
THREAD_COUNT=4
REPORT_FORMAT="html,json"

while [[ $# -gt 0 ]]; do
  case $1 in
    --port)
      API_PORT="$2"
      shift 2
      ;;
    --modules)
      TEST_MODULES="$2"
      shift 2
      ;;
    --sequential)
      PARALLEL=false
      shift
      ;;
    --threads)
      THREAD_COUNT="$2"
      shift 2
      ;;
    --report)
      REPORT_FORMAT="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

export RAG_API_URL="http://localhost:${API_PORT}"
export PARALLEL_TESTS="${THREAD_COUNT}"
export REPORT_FORMAT="${REPORT_FORMAT}"

echo "=== RAG-LLM Framework Deployment and Testing ==="

PORT_CHECK=$(lsof -i:${API_PORT} -t || echo "")
if [ ! -z "$PORT_CHECK" ]; then
  echo "Port ${API_PORT} is already in use by process ${PORT_CHECK}. Killing process..."
  kill -9 $PORT_CHECK || true
  sleep 2
fi

echo "Starting API server on port ${API_PORT}..."

python -m uvicorn src.backend.main:app --host 0.0.0.0 --port ${API_PORT} &
API_PID=$!

echo "Waiting for API to start..."
sleep 5

echo "Verifying deployment..."
python tests/post_deployment/verify_deployment.py --url "${RAG_API_URL}" --retries 5 --delay 2
VERIFY_STATUS=$?

if [ $VERIFY_STATUS -ne 0 ]; then
  echo "Deployment verification failed. Stopping API server."
  kill $API_PID 2>/dev/null || true
  exit 1
fi

echo "Running post-deployment tests..."
SEQUENTIAL_ARG=""
if [ "${PARALLEL}" = "false" ]; then
  SEQUENTIAL_ARG="--sequential"
fi

python tests/post_deployment/run_tests.py ${SEQUENTIAL_ARG} --modules "${TEST_MODULES}"
TEST_STATUS=$?

echo "Stopping API server..."
kill $API_PID 2>/dev/null || true

exit $TEST_STATUS
