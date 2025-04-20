#
#
#
#
#

set -e

PORT=8080

while [[ $# -gt 0 ]]; do
  case $1 in
    --port)
      PORT="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
WEB_DIR="$PROJECT_ROOT/src/web"

if [ ! -d "$WEB_DIR" ]; then
  echo "Error: Web UI directory not found at $WEB_DIR"
  exit 1
fi

echo "Starting web UI server on port $PORT..."
echo "You can access the UI at http://localhost:$PORT"
echo "Press Ctrl+C to stop the server"

cd "$WEB_DIR" && python3 -m http.server "$PORT"
