set -e

echo "Preparing to share the complete package..."

if [ ! -f "/home/ubuntu/rag-llm-complete-package.zip" ]; then
  echo "Error: Package file not found. Run create-complete-package.sh first."
  exit 1
fi

SHARE_DIR="/home/ubuntu/rag-llm-framework/share-info"
mkdir -p $SHARE_DIR

cp /home/ubuntu/rag-llm-complete-package.zip $SHARE_DIR/

cat > $SHARE_DIR/README.txt << EOF

This package contains all files needed to run the RAG-LLM Framework in:
- Local development environment
- Docker Compose environment
- Kubernetes environment


1. Unzip the package:
   \`\`\`
   unzip rag-llm-complete-package.zip
   \`\`\`

2. Navigate to the project directory:
   \`\`\`
   cd rag-llm-framework
   \`\`\`

3. Copy your Zscaler certificate (if needed):
   \`\`\`
   cp /path/to/your/zscaler.crt .
   \`\`\`

4. Create a .env file from the example:
   \`\`\`
   cp .env.example .env
   \`\`\`

5. Run with Docker Compose:
   \`\`\`
   make build
   make up
   \`\`\`

6. Test the certificate installation:
   \`\`\`
   ./scripts/test-certificate.sh
   \`\`\`

7. Access the API at http://localhost:8000

For detailed instructions, see the README.md and docs/ directory.
EOF

echo "Package prepared for sharing at $SHARE_DIR"
echo "You can now download the package and instructions from this location."
