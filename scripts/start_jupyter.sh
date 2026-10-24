#!/usr/bin/env bash
# Jupyter Lab을 로컬(127.0.0.1)에서만 띄운다. Jupyter MCP가 여기에 붙는다.
# 토큰/포트는 .mcp.json의 JUPYTER_TOKEN / JUPYTER_URL과 같아야 한다.
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-.venv/bin/python}"
ROOTFLAG=""
[ "$(id -u)" = "0" ] && ROOTFLAG="--allow-root"   # root로 돌릴 때 Jupyter가 요구
exec "$PY" -m jupyter lab \
  --no-browser \
  --ip 127.0.0.1 \
  --port "${JUPYTER_PORT:-8888}" \
  --IdentityProvider.token "${JUPYTER_TOKEN:-acdc-local}" \
  --ServerApp.root_dir "$(pwd)" \
  $ROOTFLAG "$@"
