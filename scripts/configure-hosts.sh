set -e

HOST="rag-llm.local"

if ! grep -q "$HOST" /etc/hosts; then
    echo "Adding $HOST to /etc/hosts..."
    echo "127.0.0.1 $HOST" | sudo tee -a /etc/hosts
else
    echo "$HOST already in /etc/hosts"
fi
