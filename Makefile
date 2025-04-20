# RAG-LLM Framework Makefile

# Variables
NAMESPACE ?= rag-llm
ENV_FILE ?= .env
KUBE_CONTEXT ?= $(shell kubectl config current-context)

# Docker image names
BACKEND_IMAGE := rag-llm-backend:latest
SLACKBOT_IMAGE := rag-llm-slackbot:latest
MODEL_CONTROLLER_IMAGE := rag-llm-model-controller:latest

# Storage configuration
STORAGE_TYPE ?= local
CLOUD_PROVIDER ?= s3
CACHE_DIR ?= /tmp/ollama_cache

# Local development settings
BACKEND_PORT ?= 8000
WEB_UI_PORT ?= 8080

# Helm chart path
HELM_CHART_PATH := ./helm/rag-llm-framework

# Default target
.PHONY: all
all: help

# Help target
.PHONY: help
help:
	@echo "RAG-LLM Framework Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make setup              Setup the RAG-LLM framework in Kubernetes"
	@echo "  make build              Build Docker images"
	@echo "  make deploy             Deploy to Kubernetes using Helm"
	@echo "  make load-secrets       Load secrets from .env file to Kubernetes"
	@echo "  make clean              Remove deployed resources"
	@echo "  make stop               Stop all pods and remove namespace (alias for clean)"
	@echo "  make logs               View logs from backend and Ollama pods"
	@echo "  make status             Check status of deployed pods"
	@echo "  make pull-model         Pull Ollama model"
	@echo "  make fix-resources      Apply reduced resource requirements for Kubernetes"
	@echo "  make fix-import         Fix import error in backend pod"
	@echo "  make test-import        Test import paths in backend pod"
	@echo ""
	@echo "Local Development Commands:"
	@echo "  make run-backend        Start the backend API server locally"
	@echo "  make run-web-ui         Start the web UI server locally"
	@echo "  make run-all            Start both backend and web UI servers"
	@echo "  make test-chat          Test the chat endpoints"
	@echo ""
	@echo "Storage Configuration Commands:"
	@echo "  make configure-storage   Configure storage type (local or cloud)"
	@echo "  make build-model-controller Build model controller Docker image"
	@echo "  make deploy-cloud-storage Deploy with cloud storage configuration"
	@echo ""
	@echo "Docker Compose Commands:"
	@echo "  make up                 Start services with Docker Compose"
	@echo "  make down               Stop Docker Compose services"
	@echo "  make docker-logs        View logs from Docker Compose services"
	@echo "  make test-certificate   Test Zscaler certificate installation"
	@echo ""
	@echo "Variables:"
	@echo "  NAMESPACE               Kubernetes namespace (default: rag-llm)"
	@echo "  ENV_FILE                Environment file path (default: .env)"
	@echo "  KUBE_CONTEXT            Kubernetes context (default: current context)"
	@echo "  STORAGE_TYPE            Storage type (local or cloud, default: local)"
	@echo "  CLOUD_PROVIDER          Cloud provider for storage (s3, gcs, azure, nfs, default: s3)"
	@echo "  CACHE_DIR               Cache directory for model storage (default: /tmp/ollama_cache)"
	@echo "  BACKEND_PORT            Port for the backend API server (default: 8000)"
	@echo "  WEB_UI_PORT             Port for the web UI server (default: 8080)"
	@echo ""

# Setup target
.PHONY: setup
setup: check-dependencies create-namespace build load-secrets deploy

# Check dependencies
.PHONY: check-dependencies
check-dependencies:
	@echo "Checking dependencies..."
	@command -v kubectl >/dev/null 2>&1 || { echo "kubectl is required but not installed. Aborting."; exit 1; }
	@command -v helm >/dev/null 2>&1 || { echo "helm is required but not installed. Aborting."; exit 1; }
	@command -v docker >/dev/null 2>&1 || { echo "docker is required but not installed. Aborting."; exit 1; }
	@echo "All dependencies are installed."
	@echo "Using Kubernetes context: $(KUBE_CONTEXT)"

# Create namespace
.PHONY: create-namespace
create-namespace:
	@echo "Creating namespace $(NAMESPACE) if it doesn't exist..."
	@kubectl --context $(KUBE_CONTEXT) get namespace $(NAMESPACE) >/dev/null 2>&1 || kubectl --context $(KUBE_CONTEXT) create namespace $(NAMESPACE)

# Build Docker images
.PHONY: build
build:
	@echo "Building Docker images..."
	docker build -t $(BACKEND_IMAGE) .
	docker build -t $(SLACKBOT_IMAGE) -f Dockerfile.slack .
	docker build -t rag-llm-ollama-custom:latest -f Dockerfile.ollama .

# Build model controller Docker image
.PHONY: build-model-controller
build-model-controller:
	@echo "Building model controller Docker image..."
	docker build -t $(MODEL_CONTROLLER_IMAGE) -f Dockerfile.model-controller .

# Load secrets from .env file
.PHONY: load-secrets
load-secrets:
	@if [ -f "$(ENV_FILE)" ]; then \
		echo "Loading secrets from $(ENV_FILE)..."; \
		chmod +x scripts/load-env-to-k8s.sh; \
		./scripts/load-env-to-k8s.sh --namespace $(NAMESPACE) --env-file $(ENV_FILE); \
		echo "Secrets loaded successfully."; \
	else \
		echo "Warning: $(ENV_FILE) file not found. Skipping secrets loading."; \
	fi

# Configure storage type
.PHONY: configure-storage
configure-storage:
	@echo "Configuring storage type: $(STORAGE_TYPE)"
	@if [ "$(STORAGE_TYPE)" = "cloud" ]; then \
		echo "Cloud provider: $(CLOUD_PROVIDER)"; \
		echo "Cache directory: $(CACHE_DIR)"; \
		echo "Updating configuration..."; \
		sed -i "s/type: local/type: $(STORAGE_TYPE)/g" config/config.yaml; \
		sed -i "s/provider: s3/provider: $(CLOUD_PROVIDER)/g" config/config.yaml; \
		echo "Storage configuration updated in config/config.yaml"; \
	else \
		echo "Using local storage"; \
		sed -i "s/type: cloud/type: local/g" config/config.yaml; \
		echo "Storage configuration updated to use local storage"; \
	fi

# Deploy using Helm
.PHONY: deploy
deploy:
	@echo "Deploying to Kubernetes using Helm..."
	@if [ -f "$(ENV_FILE)" ]; then \
		helm upgrade --install rag-llm-framework $(HELM_CHART_PATH) \
			--kube-context $(KUBE_CONTEXT) \
			--namespace $(NAMESPACE) \
			--set global.environment=development \
			--set backend.ingress.hosts[0].host=rag-llm.local \
			--set backend.env[0].name=PYTHONPATH \
			--set backend.env[0].value=/app \
			--set secrets.create=false \
			--set secrets.existingSecret=$(NAMESPACE)-secrets; \
	else \
		helm upgrade --install rag-llm-framework $(HELM_CHART_PATH) \
			--kube-context $(KUBE_CONTEXT) \
			--namespace $(NAMESPACE) \
			--set global.environment=development \
			--set backend.ingress.hosts[0].host=rag-llm.local \
			--set backend.env[0].name=PYTHONPATH \
			--set backend.env[0].value=/app; \
	fi
	@echo "Deployment complete."

# Deploy with cloud storage configuration
.PHONY: deploy-cloud-storage
deploy-cloud-storage:
	@echo "Deploying with cloud storage configuration..."
	@if [ -f "$(ENV_FILE)" ]; then \
		helm upgrade --install rag-llm-framework $(HELM_CHART_PATH) \
			--kube-context $(KUBE_CONTEXT) \
			--namespace $(NAMESPACE) \
			--set global.environment=development \
			--set backend.ingress.hosts[0].host=rag-llm.local \
			--set secrets.create=false \
			--set secrets.existingSecret=$(NAMESPACE)-secrets \
			--set ollama.persistence.storage.type=$(STORAGE_TYPE) \
			--set ollama.persistence.storage.cloud.provider=$(CLOUD_PROVIDER); \
	else \
		echo "Error: $(ENV_FILE) file not found. Required for cloud storage configuration."; \
		exit 1; \
	fi
	@echo "Deployment with cloud storage complete."

# Configure hosts file
.PHONY: configure-hosts
configure-hosts:
	@echo "Configuring hosts file..."
	@chmod +x scripts/configure-hosts.sh
	@./scripts/configure-hosts.sh

# Pull Ollama model
.PHONY: pull-model
pull-model:
	@echo "Pulling Ollama model (this may take a while)..."
	@chmod +x scripts/pull-ollama-model.sh
	@./scripts/pull-ollama-model.sh $(NAMESPACE) llama2

# View logs
.PHONY: logs
logs:
	@echo "Viewing logs from backend pod..."
	@BACKEND_POD=$$(kubectl --context $(KUBE_CONTEXT) get pod -l app=rag-llm-backend -n $(NAMESPACE) -o jsonpath="{.items[0].metadata.name}") && \
	kubectl --context $(KUBE_CONTEXT) logs -f $$BACKEND_POD -n $(NAMESPACE)

# Check status
.PHONY: status
status:
	@echo "Checking status of deployed pods..."
	@kubectl --context $(KUBE_CONTEXT) get pods -n $(NAMESPACE)

# Clean up
.PHONY: clean
clean:
	@echo "Removing deployed resources..."
	@helm --kube-context $(KUBE_CONTEXT) uninstall rag-llm-framework -n $(NAMESPACE) || true
	@kubectl --context $(KUBE_CONTEXT) delete namespace $(NAMESPACE) || true
	@echo "Cleanup complete."

# Stop all pods and remove namespace (alias for clean)
.PHONY: stop
stop: clean

# Fix resource limits for Kubernetes deployment
.PHONY: fix-resources
fix-resources:
	@echo "Applying reduced resource requirements..."
	@chmod +x scripts/fix-resource-limits-updated.sh
	@./scripts/fix-resource-limits-updated.sh

	@./scripts/fix-ollama-connection.sh

# Fix import error in backend pod
.PHONY: fix-import
fix-import:
	@echo "Fixing import error in backend pod..."
	@chmod +x scripts/fix-import-error.sh
	@./scripts/fix-import-error.sh

# Test import paths in backend pod
.PHONY: test-import
test-import:
	@echo "Testing import paths in backend pod..."
	@chmod +x scripts/test-import-paths.sh
	@./scripts/test-import-paths.sh $(NAMESPACE)

	@./scripts/fix-ollama-connection.sh

# Fix Ollama connection in backend pod
.PHONY: fix-ollama-connection
fix-ollama-connection:
	@echo "Fixing Ollama connection in backend pod..."
	@chmod +x scripts/fix-ollama-connection.sh
	@./scripts/fix-ollama-connection.sh

# Docker Compose Commands
.PHONY: up
up:
	@echo "Starting services with Docker Compose..."
	docker-compose up -d

.PHONY: down
down:
	@echo "Stopping services..."
	docker-compose down

.PHONY: docker-logs
docker-logs:
	@echo "Viewing logs from Docker Compose services..."
	docker-compose logs -f

.PHONY: test-certificate
test-certificate:
	@echo "Testing Zscaler certificate installation..."
	@chmod +x scripts/test-certificate.sh
	@./scripts/test-certificate.sh

# Local Development Commands
# Run backend API server
.PHONY: run-backend
run-backend:
	@echo "Starting backend API server on port $(BACKEND_PORT)..."
	@chmod +x scripts/run-local-native.sh
	@./scripts/run-local-native.sh

# Run web UI server
.PHONY: run-web-ui
run-web-ui:
	@echo "Starting web UI server on port $(WEB_UI_PORT)..."
	@chmod +x scripts/run-web-ui.sh
	@./scripts/run-web-ui.sh --port $(WEB_UI_PORT)

# Run both backend and web UI
.PHONY: run-all
run-all:
	@echo "Starting both backend and web UI servers..."
	@chmod +x scripts/run-local-native.sh
	@./scripts/run-local-native.sh &
	@echo "Backend server started. Waiting for it to initialize..."
	@sleep 5
	@echo "Starting web UI server..."
	@chmod +x scripts/run-web-ui.sh
	@./scripts/run-web-ui.sh --port $(WEB_UI_PORT)

# Test chat endpoints
.PHONY: test-chat
test-chat:
	@echo "Testing chat endpoints..."
	@python scripts/test-chat-endpoints.py --base-url http://localhost:$(BACKEND_PORT)
