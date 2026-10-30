#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
if [[ ! -x .venv/bin/python || ! -f terminal/web/dist/index.html ]]; then
  printf 'Run bash scripts/setup_terminal.sh first. Existing sources/data are preserved.\n' >&2
  exit 1
fi
# Never leave the user looking at an older process after a failed second start.
.venv/bin/python - <<'PYTHON'
import socket
try:
    connection = socket.create_connection(('127.0.0.1', 8787), timeout=1)
except OSError:
    pass
else:
    connection.close()
    raise SystemExit('Port 8787 is already in use. Stop the existing GIG server with Ctrl+C in its terminal, then restart. No process was killed or replaced.')
import msgpack
if msgpack.version < (1, 2, 3):
    raise SystemExit('Security dependency update required: run .venv/bin/python -m pip install -r terminal/server/requirements.txt. Existing SEC configuration and keys are unchanged.')
PYTHON
# Safe readiness only;private JSON is independently loaded by the backend as well.
.venv/bin/python scripts/configure_sec.py --check
exec .venv/bin/python -m terminal.server
