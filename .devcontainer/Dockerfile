FROM mcr.microsoft.com/devcontainers/cpp:1-ubuntu-24.04@sha256:d51703c4fcbe93cd889d38005847521d87cca4d304f33423430daf10a384a332
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.12-dev python3.12-venv ninja-build \
    && rm -rf /var/lib/apt/lists/*
