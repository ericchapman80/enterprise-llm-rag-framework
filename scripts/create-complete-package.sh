set -e

echo "Creating comprehensive package with all changes..."

cd /home/ubuntu
zip -r rag-llm-complete-package.zip rag-llm-framework -x "rag-llm-framework/.git/*" "rag-llm-framework/__pycache__/*" "rag-llm-framework/rag-llm-env/*" "rag-llm-framework/*.zip"

echo "Package created at /home/ubuntu/rag-llm-complete-package.zip"
echo "This package includes all files for local, Docker, and Kubernetes testing."
