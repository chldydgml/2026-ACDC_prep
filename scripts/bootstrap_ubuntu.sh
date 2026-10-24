#!/usr/bin/env bash
# Ubuntu / WSL2 Ubuntu / VMware·VirtualBox 게스트에서 선행 도구 + 프로젝트 가상환경을
# 한 번에 세팅한다. 멱등(이미 있으면 건너뜀). 저장소를 클론한 뒤 그 안에서 실행한다.
#
#   sudo apt update && sudo apt install -y git curl   # git/curl 이 없을 때만 (클론 전에)
#   git clone https://github.com/chldydgml/2026-acdc_prep.git && cd 2026-acdc_prep
#   scripts/bootstrap_ubuntu.sh            # 기본: 선행도구 + .venv (torch 제외)
#   scripts/bootstrap_ubuntu.sh --torch    # 적대적 이미지 문제용 CPU torch까지
set -euo pipefail
cd "$(dirname "$0")/.."

WITH_TORCH=0
[ "${1:-}" = "--torch" ] && WITH_TORCH=1

# root면 그대로, 아니면 sudo 로 실행 (파이프 `| sudo -E bash` 문제 회피)
run_root() { if [ "$(id -u)" -ne 0 ]; then sudo "$@"; else "$@"; fi; }
export DEBIAN_FRONTEND=noninteractive

echo "== [1/5] apt 패키지 (curl git gnupg) =="
run_root apt-get update -y
run_root apt-get install -y curl git gnupg

echo "== [2/5] uv (파이썬 3.12 포함) =="
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
export PATH="$HOME/.local/bin:$PATH"
uv --version

echo "== [3/5] Node.js 22 LTS (context7 MCP의 npx 용) =="
need_node=1
if command -v node >/dev/null 2>&1; then
  major="$(node -p 'process.versions.node.split(".")[0]' 2>/dev/null || echo 0)"
  [ "$major" -ge 20 ] && need_node=0
fi
if [ "$need_node" = 1 ]; then
  curl -fsSL https://deb.nodesource.com/setup_22.x | run_root bash -
  run_root apt-get install -y nodejs
fi
node --version

echo "== [4/5] Claude Code (네이티브 설치) =="
if ! command -v claude >/dev/null 2>&1 && [ ! -x "$HOME/.local/bin/claude" ]; then
  curl -fsSL https://claude.ai/install.sh | bash
fi
claude --version 2>/dev/null || "$HOME/.local/bin/claude" --version 2>/dev/null \
  || echo "  (claude: 새 터미널을 열고 'claude --version' 으로 확인)"

echo "== [5/5] 프로젝트 가상환경 (.venv) =="
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python -r requirements.txt
if [ "$WITH_TORCH" = 1 ]; then
  echo "  + CPU 전용 torch/torchvision"
  uv pip install --python .venv/bin/python torch torchvision \
    --index-url https://download.pytorch.org/whl/cpu
fi

echo
echo "[완료] 다음 단계 — 새 터미널을 열고:"
echo "  터미널 A:  scripts/start_jupyter.sh                 (실험실 전원, 끄지 말 것)"
echo "  터미널 B:  claude    (처음이면 로그인 → MCP 승인 → /mcp 로 connected 확인)"
echo "  브라우저:  http://127.0.0.1:8888/lab?token=acdc-local   (VM이면 VM 안의 브라우저로)"
echo
echo "  * uv/claude 가 'command not found' 면 새 터미널을 열거나:  source \$HOME/.local/bin/env"
