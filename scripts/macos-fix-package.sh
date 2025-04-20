
set -e

echo "=== Creating macOS Fix Package ==="

mkdir -p macos-memory-fix-package

cp scripts/fix-memory-issue-macos.sh macos-memory-fix-package/
cp scripts/run-local-native-small-model-macos.sh macos-memory-fix-package/
cp macos-memory-fix.patch macos-memory-fix-package/
cp docs/memory-requirements.md macos-memory-fix-package/
cp docs/memory-fix-guide.md macos-memory-fix-package/
cp docs/ollama-installation.md macos-memory-fix-package/
cp scripts/install-ollama.sh macos-memory-fix-package/
cp scripts/verify-model.sh macos-memory-fix-package/

cat > macos-memory-fix-package/README.md << 'EOF'

This package contains macOS-compatible scripts and documentation to fix the memory issue in the RAG-LLM Framework where the default llama2 model requires more memory (8.4 GiB) than may be available on some systems.


1. `memory-requirements.md` - Documentation on memory requirements for different LLM models
2. `memory-fix-guide.md` - Guide on applying the memory fix
3. `ollama-installation.md` - Instructions for installing Ollama
4. `fix-memory-issue-macos.sh` - Script to automatically apply all necessary changes (macOS compatible)
5. `run-local-native-small-model-macos.sh` - Script to run the application with the tinyllama model (macOS compatible)
6. `macos-memory-fix.patch` - Patch file to modify the existing run-local-native.sh script
7. `install-ollama.sh` - Script to install Ollama
8. `verify-model.sh` - Script to verify the model configuration



1. Copy `fix-memory-issue-macos.sh` to your RAG-LLM Framework root directory
2. Make it executable: `chmod +x fix-memory-issue-macos.sh`
3. Run it: `./fix-memory-issue-macos.sh`


1. Copy `run-local-native-small-model-macos.sh` to your RAG-LLM Framework scripts directory
2. Make it executable: `chmod +x scripts/run-local-native-small-model-macos.sh`
3. Run it: `./scripts/run-local-native-small-model-macos.sh`


1. Copy `macos-memory-fix.patch` to your RAG-LLM Framework root directory
2. Apply the patch: `patch -p0 < macos-memory-fix.patch`


Copy the documentation files to your RAG-LLM Framework docs directory for reference on memory requirements and installation instructions.


After applying the fix, you should be able to run the application without encountering the memory error. The application will use the tinyllama model which requires only about 1.2 GiB of memory instead of the 8.4 GiB required by llama2.


If you encounter any issues, please refer to the documentation files for troubleshooting tips. You can also run the `verify-model.sh` script to check your model configuration.
EOF

zip -r macos-memory-fix-package.zip macos-memory-fix-package/

echo "macOS fix package created: macos-memory-fix-package.zip"
echo "You can share this package with users who are experiencing sed syntax issues on macOS."
