# Ollama Installation Guide

This guide provides instructions for installing Ollama, which is required to run the RAG-LLM Framework.

## Automated Installation

We provide a script to automatically install Ollama and pull the required model:

```bash
# Make the script executable
chmod +x scripts/install-ollama.sh

# Run the installation script
./scripts/install-ollama.sh
```

## Manual Installation

### macOS

```bash
# Using Homebrew
brew install ollama

# Start the Ollama service
ollama serve
```

### Linux

```bash
# Using the official installation script
curl -fsSL https://ollama.com/install.sh | sh

# Start the Ollama service
systemctl --user start ollama
# or
ollama serve
```

### Windows

1. Download the installer from [https://ollama.com/download](https://ollama.com/download)
2. Run the installer and follow the instructions
3. Start Ollama from the Start menu

## Pulling the Required Model

After installing Ollama, you need to pull the model:

```bash
# Pull the tinyllama model (recommended for systems with limited memory)
ollama pull tinyllama

# Or pull the llama2 model (requires ~8.4 GiB of memory)
ollama pull llama2
```

## Verifying the Installation

You can verify that Ollama is installed and running correctly:

```bash
# Make the verification script executable
chmod +x scripts/verify-model.sh

# Run the verification script
./scripts/verify-model.sh
```

## Troubleshooting

If you encounter issues with Ollama:

1. Ensure the Ollama service is running:
   ```bash
   curl http://localhost:11434/api/version
   ```

2. Check available models:
   ```bash
   ollama list
   ```

3. Check system memory:
   ```bash
   free -h
   ```

4. If you see memory errors, switch to a smaller model:
   ```bash
   ./scripts/fix-memory-issue.sh
   ```

For more information on memory requirements, see [memory-requirements.md](memory-requirements.md).
