#!/usr/bin/env bash
# Build the existing authored diagnostics used by terminal/historical.py.
# Never reads market data or enables a provider. Requires zlib >=1.3.1.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
build_dir="${GIG_TERMINAL_NATIVE_BUILD:-$PWD/build/phase9-clean-release}"
cmake -S . -B "$build_dir" -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_CXX_COMPILER=g++ \
  -DGIG_BUILD_ITCH_STREAMING=ON
cmake --build "$build_dir" --target gig_itch_validation_demo gig_lobster_validate -j2
