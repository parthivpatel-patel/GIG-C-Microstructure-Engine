#!/usr/bin/env bash
# Builds existing sources in an owner-created development environment; no hosting/data acquisition.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
for tool in python3.12 g++ cmake ninja node npm; do
  command -v "$tool" >/dev/null || { printf 'Missing %s. Use the repository Codespaces configuration.\n' "$tool" >&2; exit 1; }
done
node -e 'if(Number(process.versions.node.split(".")[0])<24)throw Error("Node24 or newer required")'
if [[ -e .venv && ! -x .venv/bin/python ]]; then
  printf 'Existing .venv is not usable; preserving it. Choose a clean development environment.\n' >&2
  exit 1
fi
if [[ ! -e .venv ]]; then python3.12 -m venv .venv; fi
.venv/bin/python -c 'import sys; assert sys.version_info[:2] == (3,12), "Existing .venv needs Python3.12; preserving it rather than replacing it"'
.venv/bin/python -m pip install -r requirements-python.lock -r terminal/server/requirements.txt
CXX=g++ .venv/bin/python -m pip install --no-build-isolation .
npm --prefix terminal/web ci --ignore-scripts
npm --prefix terminal/web run build
.venv/bin/python -c 'import gig_microstructure as g; assert hasattr(g._native,"AggregateDepth"); print("Actual native engine ready:",g.native_build_info())'
printf '\nSetup complete. Start: bash scripts/start_terminal.sh\nNo observed data or live provider connection has been enabled.\n'
