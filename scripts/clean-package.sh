set -e

echo "Cleaning package before final zip creation..."

find /home/ubuntu/rag-llm-framework -name "__pycache__" -type d -exec rm -rf {} +
find /home/ubuntu/rag-llm-framework -name "*.pyc" -delete

find /home/ubuntu/rag-llm-framework -name "*.tmp" -delete
find /home/ubuntu/rag-llm-framework -name "*.bak" -delete

echo "Package cleaned. Ready for final zip creation."
