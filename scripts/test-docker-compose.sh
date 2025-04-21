#!/bin/bash
set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

KEEP_RUNNING=false
COMPOSE_FILE="docker-compose.test.yml"
MAX_RETRIES=5
RETRY_DELAY=5

while [[ $# -gt 0 ]]; do
  case $1 in
    --keep-running)
      KEEP_RUNNING=true
      shift
      ;;
    --compose-file)
      COMPOSE_FILE="$2"
      shift 2
      ;;
    --max-retries)
      MAX_RETRIES="$2"
      shift 2
      ;;
    --retry-delay)
      RETRY_DELAY="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

echo -e "${GREEN}=== Testing Docker Compose Deployment ===${NC}"

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null || ! command -v docker-compose &> /dev/null; then
  echo -e "${RED}Docker or Docker Compose not installed. Exiting.${NC}"
  exit 1
fi

if [ "$KEEP_RUNNING" = true ]; then
  echo "Using current directory for deployment (--keep-running mode)..."
  touch .docker_compose_running
fi

# Clean up function that respects the --keep-running flag
function cleanup {
  if [ "$KEEP_RUNNING" = false ]; then
    echo "Cleaning up Docker Compose services..."
    docker-compose -f ${COMPOSE_FILE} down
  else
    echo "Keeping Docker Compose services running for further testing..."
  fi
}

trap cleanup EXIT

# Build and start the backend service
echo "Building and starting backend service..."
echo "This may take several minutes for the first build..."

# Set a timeout for the build process (5 minutes)
timeout 300 docker-compose -f ${COMPOSE_FILE} build || {
  echo -e "${YELLOW}Docker Compose build timed out after 5 minutes.${NC}"
  echo -e "${YELLOW}This is expected for the first build with large dependencies.${NC}"
  exit 1
}

echo "Starting Docker Compose backend service..."
docker-compose -f ${COMPOSE_FILE} up -d --force-recreate

echo "Waiting for service to start..."
for i in $(seq 1 $MAX_RETRIES); do
  echo "Checking service status (attempt $i/$MAX_RETRIES)..."
  
  if docker-compose -f ${COMPOSE_FILE} ps | grep -q "Up"; then
    echo -e "${GREEN}Service is running!${NC}"
    break
  fi
  
  if [ $i -eq $MAX_RETRIES ]; then
    echo -e "${RED}Service failed to start after $MAX_RETRIES attempts.${NC}"
    docker-compose -f ${COMPOSE_FILE} logs
    exit 1
  fi
  
  echo "Waiting ${RETRY_DELAY} seconds before next check..."
  sleep $RETRY_DELAY
done

# Test the API endpoint with retries
echo "Testing API endpoint..."
TEST_PORT=${TEST_PORT:-8001}
echo "Using port: ${TEST_PORT}"

for i in $(seq 1 $MAX_RETRIES); do
  echo "Checking API health (attempt $i/$MAX_RETRIES)..."
  
  HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:${TEST_PORT}/health || echo "000")
  
  if [ "$HEALTH_CHECK" == "200" ]; then
    echo -e "${GREEN}API health check passed! (Status: $HEALTH_CHECK)${NC}"
    break
  fi
  
  if [ $i -eq $MAX_RETRIES ]; then
    echo -e "${RED}API health check failed after $MAX_RETRIES attempts. (Status: $HEALTH_CHECK)${NC}"
    docker-compose -f ${COMPOSE_FILE} logs
    exit 1
  fi
  
  echo "Waiting ${RETRY_DELAY} seconds before next check..."
  sleep $RETRY_DELAY
done

echo -e "${GREEN}Docker Compose deployment test completed successfully!${NC}"
echo -e "Services are running at: ${GREEN}http://localhost:8000${NC}"

if [ "$KEEP_RUNNING" = true ]; then
  echo -e "${YELLOW}Services will remain running for further testing.${NC}"
  echo -e "To stop services manually, run: ${GREEN}docker-compose down${NC}"
fi
