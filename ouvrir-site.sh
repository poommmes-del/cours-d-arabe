#!/usr/bin/env bash
set -euo pipefail

HOST="127.0.0.1"
PORT="8765"
URL="http://${HOST}:${PORT}/site/"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG="${XDG_RUNTIME_DIR:-/tmp}/cours-arabe-http-${PORT}.log"

port_open() {
  python3 - "$HOST" "$PORT" <<'PY'
import socket
import sys

host = sys.argv[1]
port = int(sys.argv[2])

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.settimeout(0.2)
    raise SystemExit(0 if sock.connect_ex((host, port)) == 0 else 1)
PY
}

if ! port_open; then
  (
    cd "$ROOT"
    nohup python3 -m http.server "$PORT" --bind "$HOST" >"$LOG" 2>&1 &
  )

  for _ in {1..30}; do
    if port_open; then
      break
    fi
    sleep 0.1
  done
fi

xdg-open "$URL" >/dev/null 2>&1 &
