#!/bin/bash
set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Testing Docker Compose Deployment ===${NC}"

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null || ! command -v docker-compose &> /dev/null; then
  echo -e "${RED}Docker or Docker Compose not installed. Exiting.${NC}"
  exit 1
fi

TEST_DIR=$(mktemp -d)
echo "Creating isolated test environment in ${TEST_DIR}..."

cp -r src config docker-compose.test.yml Dockerfile "${TEST_DIR}/"

# Clean up on exit
function cleanup {
  echo "Cleaning up..."
  docker-compose -f "${TEST_DIR}/docker-compose.test.yml" down
  rm -rf "${TEST_DIR}"
}
trap cleanup EXIT

cd "${TEST_DIR}"

# Build and start the backend service only
echo "Building and starting backend service..."
echo "This may take several minutes for the first build..."

# Set a timeout for the build process (5 minutes)
timeout 300 docker-compose -f docker-compose.test.yml build || {
  echo -e "${YELLOW}Docker Compose build timed out after 5 minutes.${NC}"
  echo -e "${YELLOW}This is expected for the first build with large dependencies.${NC}"
  exit 1
}

echo "Starting Docker Compose backend service..."
docker-compose -f docker-compose.test.yml up -d

echo "Waiting for service to start..."
sleep 15

# Check if service is running
if ! docker-compose -f docker-compose.test.yml ps | grep -q "Up"; then
  echo -e "${RED}Docker Compose service failed to start properly.${NC}"
  docker-compose -f docker-compose.test.yml logs
  exit 1
fi

# Test the API endpoint with proper HTTP status code check
echo "Testing API endpoint..."
HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)

if [ "$HEALTH_CHECK" == "200" ]; then
  echo -e "${GREEN}API health check passed! (Status: $HEALTH_CHECK)${NC}"
else
  echo -e "${RED}API health check failed! (Status: $HEALTH_CHECK)${NC}"
  docker-compose -f docker-compose.test.yml logs
  exit 1
fi

echo -e "${GREEN}Docker Compose deployment test completed successfully!${NC}"
cd -
