#!/bin/bash
#
# Script Name: load-env-to-k8s.sh
#
#
#
#
# Notes:
#


set -e

NAMESPACE="rag-llm"
SECRET_NAME="rag-llm-secrets"
ENV_FILE=".env"

while [[ $# -gt 0 ]]; do
  case $1 in
    --namespace)
      NAMESPACE="$2"
      shift 2
      ;;
    --secret-name)
      SECRET_NAME="$2"
      shift 2
      ;;
    --env-file)
      ENV_FILE="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

if [ ! -f "$ENV_FILE" ]; then
  echo "Error: .env file not found at $ENV_FILE"
  exit 1
fi

kubectl get namespace "$NAMESPACE" &>/dev/null || kubectl create namespace "$NAMESPACE"

kubectl -n "$NAMESPACE" get secret "$SECRET_NAME" &>/dev/null && kubectl -n "$NAMESPACE" delete secret "$SECRET_NAME"

kubectl -n "$NAMESPACE" create secret generic "$SECRET_NAME" --from-env-file="$ENV_FILE"

echo "Secret $SECRET_NAME created in namespace $NAMESPACE from $ENV_FILE"
