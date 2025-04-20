

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
API_URL=${API_URL:-"http://localhost:8000"}

if [ -f "$PROJECT_ROOT/.env" ]; then
    echo "Loading environment variables from .env file..."
    export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs)
fi

if [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: GITHUB_TOKEN environment variable is not set."
    echo "Please set it in your .env file or export it before running this script."
    exit 1
fi

echo "Refreshing GitHub repositories..."

curl -X POST "$API_URL/ingest-repos" \
    -H "Content-Type: application/json" \
    -d '{}'

echo ""
echo "GitHub repositories refresh completed."
echo "You can schedule this script in a cron job to periodically update the knowledge base:"
echo ""
echo "# Example cron job (runs every day at 2 AM)"
echo "0 2 * * * $PROJECT_ROOT/scripts/refresh-github-repos.sh >> $PROJECT_ROOT/logs/github-refresh.log 2>&1"
