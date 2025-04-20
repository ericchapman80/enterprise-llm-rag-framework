#!/bin/bash

set -e

NAMESPACE="rag-llm"
KUBE_CONTEXT=$(kubectl config current-context)

echo "=== Fixing Backend Deployment in Kubernetes ==="

# Step 1: Fix the import paths in main.py
echo "Fixing import paths in main.py..."
kubectl --context $KUBE_CONTEXT exec -n $NAMESPACE $(kubectl --context $KUBE_CONTEXT get pod -n $NAMESPACE -l app=rag-llm-backend -o jsonpath='{.items[0].metadata.name}') -- sed -i 's/from rag_engine import RAGEngine/from src.backend.rag_engine import RAGEngine/g' /app/src/backend/main.py
kubectl --context $KUBE_CONTEXT exec -n $NAMESPACE $(kubectl --context $KUBE_CONTEXT get pod -n $NAMESPACE -l app=rag-llm-backend -o jsonpath='{.items[0].metadata.name}') -- sed -i 's/from data_ingestion import DataIngestionManager/from src.backend.data_ingestion import DataIngestionManager/g' /app/src/backend/main.py

# Step 2: Fix the Ollama connection
echo "Fixing Ollama connection..."
OLLAMA_SERVICE=$(kubectl --context $KUBE_CONTEXT get service -n $NAMESPACE -l app=ollama -o jsonpath='{.items[0].metadata.name}')
echo "Ollama service: $OLLAMA_SERVICE"

# Update the ConfigMap with the correct Ollama URL
echo "Updating ConfigMap with correct Ollama URL..."
kubectl --context $KUBE_CONTEXT get configmap -n $NAMESPACE rag-llm-framework-config -o yaml > /tmp/configmap.yaml
sed -i "s|base_url: http://localhost:11434|base_url: http://$OLLAMA_SERVICE:11434|g" /tmp/configmap.yaml
kubectl --context $KUBE_CONTEXT apply -f /tmp/configmap.yaml

# Step 3: Restart the backend pod
echo "Restarting backend pod..."
kubectl --context $KUBE_CONTEXT rollout restart deployment -n $NAMESPACE rag-llm-backend

echo "Waiting for backend pod to restart..."
kubectl --context $KUBE_CONTEXT rollout status deployment -n $NAMESPACE rag-llm-backend --timeout=120s

echo "=== Checking backend pod status ==="
kubectl --context $KUBE_CONTEXT get pods -n $NAMESPACE -l app=rag-llm-backend

echo "=== Fix complete! ==="
echo "You can test the backend with: curl http://rag-llm.local/health"
