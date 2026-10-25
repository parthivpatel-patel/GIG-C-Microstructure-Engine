#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
if [[ ! -x .venv/bin/python || ! -f terminal/web/dist/index.html ]]; then
  printf 'Run bash scripts/setup_terminal.sh first. Existing sources/data are preserved.\n' >&2
  exit 1
fi
exec .venv/bin/python -m terminal.server
