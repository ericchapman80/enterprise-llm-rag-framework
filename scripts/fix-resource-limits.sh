#!/bin/bash
# Script to fix resource limits and redeploy

set -e

NAMESPACE="rag-llm"

echo "=== Updating Helm deployment with reduced resource requirements ==="
helm upgrade --install rag-llm-framework ./helm/rag-llm-framework \
  --namespace $NAMESPACE \
  --set backend.resources.requests.cpu=100m \
  --set backend.resources.requests.memory=512Mi \
  --set backend.resources.limits.cpu=500m \
  --set backend.resources.limits.memory=1Gi \
  --set ollama.resources.requests.cpu=100m \
  --set ollama.resources.requests.memory=512Mi \
  --set ollama.resources.limits.cpu=500m \
  --set ollama.resources.limits.memory=1Gi

echo "=== Checking pod status after update ==="
kubectl get pods -n $NAMESPACE

echo "=== Waiting for backend pod to start (this may take a minute) ==="
kubectl wait --for=condition=Ready pod -l app=rag-llm-backend -n $NAMESPACE --timeout=120s || true

echo "=== Checking backend pod status ==="
kubectl get pods -n $NAMESPACE -l app=rag-llm-backend

echo "=== If the pod is running, test the health endpoint ==="
echo "curl http://rag-llm.local/health"
