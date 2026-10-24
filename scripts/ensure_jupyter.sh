#!/usr/bin/env bash
# Jupyter Lab이 안 떠 있으면 백그라운드로 띄운다. 이미 떠 있으면 아무것도 안 한다.
# SessionStart 훅(.claude/settings.json)과 수동 실행에서 공용으로 쓴다.
# 터미널에 붙잡아 두고 싶으면 대신 scripts/start_jupyter.sh 를 쓸 것.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 0

PORT="${JUPYTER_PORT:-8888}"
TOKEN="${JUPYTER_TOKEN:-acdc-local}"
LOG="${TMPDIR:-/tmp}/acdc-jupyter.log"

# 이미 응답하면(어떤 HTTP 코드든) 그대로 둔다.
if curl -s -o /dev/null "http://127.0.0.1:${PORT}/api/status?token=${TOKEN}"; then
  echo "[ensure_jupyter] 이미 실행 중 (port ${PORT})"
  exit 0
fi

PY=".venv/bin/python"
if [ ! -x "$PY" ]; then
  echo "[ensure_jupyter] .venv 없음 — 먼저 SETUP.md 대로 설치 후 다시 실행. 지금은 건너뜀."
  exit 0
fi

ROOTFLAG=""
[ "$(id -u)" = "0" ] && ROOTFLAG="--allow-root"   # 컨테이너(root)에서만 필요

nohup "$PY" -m jupyter lab --no-browser --ip 127.0.0.1 --port "$PORT" \
  --IdentityProvider.token "$TOKEN" --ServerApp.root_dir "$(pwd)" $ROOTFLAG \
  >"$LOG" 2>&1 &
disown 2>/dev/null || true
echo "[ensure_jupyter] 백그라운드 시작 (port ${PORT}, log ${LOG})"
exit 0
