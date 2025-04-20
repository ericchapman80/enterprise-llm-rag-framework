#!/bin/bash

set -e

NAMESPACE="rag-llm"
KUBE_CONTEXT=$(kubectl config current-context)

echo "=== Checking backend pod status ==="
kubectl --context $KUBE_CONTEXT get pods -n $NAMESPACE -l app=rag-llm-backend

echo "=== Checking Ollama service ==="
OLLAMA_SERVICE=$(kubectl --context $KUBE_CONTEXT get service -n $NAMESPACE -l app=ollama -o jsonpath='{.items[0].metadata.name}')
OLLAMA_SERVICE_IP=$(kubectl --context $KUBE_CONTEXT get service -n $NAMESPACE $OLLAMA_SERVICE -o jsonpath='{.spec.clusterIP}')
echo "Ollama service: $OLLAMA_SERVICE"
echo "Ollama service IP: $OLLAMA_SERVICE_IP"

echo "=== Updating ConfigMap with correct Ollama URL ==="
kubectl --context $KUBE_CONTEXT get configmap -n $NAMESPACE rag-llm-framework-config -o yaml > /tmp/configmap.yaml
sed -i "s|base_url: http://localhost:11434|base_url: http://$OLLAMA_SERVICE:11434|g" /tmp/configmap.yaml
kubectl --context $KUBE_CONTEXT apply -f /tmp/configmap.yaml

echo "=== Restarting backend pod ==="
kubectl --context $KUBE_CONTEXT rollout restart deployment -n $NAMESPACE rag-llm-backend

echo "=== Waiting for backend pod to restart ==="
kubectl --context $KUBE_CONTEXT rollout status deployment -n $NAMESPACE rag-llm-backend --timeout=120s

echo "=== Checking backend pod status ==="
kubectl --context $KUBE_CONTEXT get pods -n $NAMESPACE -l app=rag-llm-backend

echo "=== Fix complete ==="
echo "If the backend pod is still not running, check the logs with:"
echo "kubectl --context $KUBE_CONTEXT logs -n $NAMESPACE -l app=rag-llm-backend"
