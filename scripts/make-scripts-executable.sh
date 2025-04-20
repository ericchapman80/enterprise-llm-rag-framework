set -e

echo "Making certificate test scripts executable..."
chmod +x scripts/test-certificate.sh
chmod +x scripts/test-k8s-certificate.sh

echo "Scripts are now executable."
echo "To test certificate in Docker: ./scripts/test-certificate.sh"
echo "To test certificate in Kubernetes: ./scripts/test-k8s-certificate.sh"
