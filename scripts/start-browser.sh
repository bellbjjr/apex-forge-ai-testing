#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -f .env ]; then
  umask 077
  python - <<'PY'
import secrets
from pathlib import Path
# VNC authentication uses the first eight characters.
Path(".env").write_text("SE_VNC_PASSWORD=" + secrets.token_hex(4) + "\n")
PY
fi

if pgrep -f "Xvfb :99" >/dev/null && pgrep -f "websockify.*7900" >/dev/null; then
  echo "The live browser service is already running. Open private forwarded port 7900."
  exit 0
fi

mkdir -p .vnc .browser-logs
password="$(sed -n 's/^SE_VNC_PASSWORD=//p' .env)"
x11vnc -storepasswd "$password" .vnc/passwd >/dev/null

export DISPLAY=:99
nohup Xvfb :99 -screen 0 1440x1000x24 -ac -noreset \
  >.browser-logs/xvfb.log 2>&1 &
nohup fluxbox >.browser-logs/fluxbox.log 2>&1 &
nohup x11vnc -display :99 -forever -shared -rfbauth .vnc/passwd -rfbport 5900 \
  >.browser-logs/x11vnc.log 2>&1 &
nohup websockify --web=/usr/share/novnc/ 7900 localhost:5900 \
  >.browser-logs/novnc.log 2>&1 &

for attempt in $(seq 1 30); do
  if python - <<'PY'
import socket
with socket.create_connection(("127.0.0.1", 7900), timeout=1):
    pass
PY
  then
    echo "The live browser is ready. Open private forwarded port 7900."
    echo "The viewing password is in your local .env file."
    exit 0
  fi
  sleep 1
done

echo "Browser viewer did not start. Inspect .browser-logs/*.log" >&2
exit 1
