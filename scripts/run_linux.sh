#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
cd "$PROJECT_DIR"

PORT=8502
URL="http://localhost:${PORT}"

# Wenn schon ein Streamlit-Server läuft: nur Browser öffnen und fertig
if curl -fsS "$URL" >/dev/null 2>&1; then
  xdg-open "$URL" >/dev/null 2>&1 || true
  exit 0
fi

# venv aktivieren (anpassen, falls anders)
source .venv/bin/activate

# Streamlit im Hintergrund starten, komplett still (kein Logfile)
nohup python -m streamlit run app.py \
  --server.port "${PORT}" \
  --server.headless true \
  --browser.gatherUsageStats false \
  >/dev/null 2>&1 &

# Warten bis Server erreichbar ist (max ~10 Sekunden)
for _ in {1..50}; do
  if curl -fsS "$URL" >/dev/null 2>&1; then
    break
  fi
  sleep 0.2
done

# Browser öffnen
xdg-open "$URL" >/dev/null 2>&1 || true
