#!/usr/bin/env bash
# scripts/dev.sh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

API_PORT="${API_PORT:-8000}"
WEB_PORT="${WEB_PORT:-5173}"
API_URL="http://localhost:${API_PORT}"

# --- helpers ---
wait_for_port() {
  local host="${1:-localhost}" port="${2:-8000}" timeout="${3:-30}"
  echo "⏳ Waiting for ${host}:${port} (timeout ${timeout}s)…"
  for i in $(seq 1 "${timeout}"); do
    if nc -z "${host}" "${port}" 2>/dev/null || curl -sf "http://${host}:${port}/health" >/dev/null 2>&1; then
      echo "✅ ${host}:${port} is ready."
      return 0
    fi
    sleep 1
  done
  echo "❌ Timeout waiting for ${host}:${port}"
  return 1
}

cleanup() {
  echo ""
  echo "🧹 Stopping dev processes…"
  # kill backend if still running
  if [[ -n "${API_PID:-}" ]] && ps -p "${API_PID}" >/dev/null 2>&1; then
    kill "${API_PID}" || true
  fi
}
trap cleanup EXIT

cd "${ROOT_DIR}"

# --- ensure python venv active (optional hint) ---
if [[ -z "${VIRTUAL_ENV:-}" ]]; then
  echo "ℹ️  Tip: activate your venv (e.g. 'source .venv/bin/activate') for best results."
fi

# --- run DB migrations (idempotent) ---
echo "🚀 Running Alembic migrations…"
python -m alembic upgrade head

# --- start API (background) ---
echo "🚀 Starting FastAPI on :${API_PORT}…"
uvicorn src.api.app:app --reload --host 0.0.0.0 --port "${API_PORT}" &
API_PID=$!

# --- wait for /health ---
wait_for_port "localhost" "${API_PORT}" 30

# --- start frontend (foreground) ---
echo "🚀 Starting frontend (Vite) on :${WEB_PORT}…"
cd frontend
# ensure API base is set; fallback to default if unset
export VITE_API_BASE_URL="${VITE_API_BASE_URL:-http://localhost:${API_PORT}}"
npm run dev