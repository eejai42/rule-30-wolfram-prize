#!/usr/bin/env bash
# Rule 30 Explorer + rulebook editor (admin portal).
#   ./start.sh          start the editor container if it is not answering, then (re)start the explorer
#   ./start.sh editor   force-restart the editor container too
#   ./start.sh build    effortless build
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

EXPLORER_PORT=7431          # hard-coded; also in explorer/vite.config.ts
EDITOR_API_PORT=42441       # pinned in effortless-rulebook/ports.env
EDITOR_UI_PORT=42442
mkdir -p .logs

start_editor() {
  echo "Starting the rulebook editor container (log: .logs/rulebook-editor.log)..."
  (cd effortless-rulebook && nohup bash edit-rulebook.sh > "$ROOT/.logs/rulebook-editor.log" 2>&1 &)
}

case "${1:-}" in
  build) effortless build; exit ;;
  editor) start_editor ;;
  "") curl -sf -m 3 "http://localhost:${EDITOR_API_PORT}/api/health" >/dev/null || start_editor ;;
  *) echo "Usage: ./start.sh [editor|build]" >&2; exit 1 ;;
esac

pids=$(lsof -ti "tcp:${EXPLORER_PORT}" 2>/dev/null || true)
[[ -n "$pids" ]] && kill -9 $pids 2>/dev/null || true

echo ""
echo "  Explorer:      http://localhost:${EXPLORER_PORT}"
echo "  Admin portal:  http://localhost:${EDITOR_UI_PORT}"
echo "  API docs:      http://localhost:${EDITOR_API_PORT}/api/docs"
echo ""
cd explorer
[[ -d node_modules ]] || npm install
exec npm run dev
