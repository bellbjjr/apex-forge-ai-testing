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
docker compose up -d
python - <<'PY'
import json, time, urllib.request
for attempt in range(60):
    try:
        with urllib.request.urlopen("http://localhost:4444/status", timeout=2) as response:
            if json.load(response)["value"]["ready"]:
                print("Selenium is ready. Open private forwarded port 7900.")
                print("The viewing password is in your local .env file.")
                break
    except (OSError, ValueError, KeyError):
        pass
    time.sleep(1)
else:
    raise SystemExit("Selenium did not become ready. Inspect: docker compose logs chrome")
PY
