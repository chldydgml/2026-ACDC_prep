#!/usr/bin/env bash
# ECC(everything-claude-code) 원본 전체를 검색용 레퍼런스로 받는다. git에는 올리지 않는다(.gitignore).
# 문제 유형이 뜨면: grep -ril "<키워드>" third_party/ecc/repo/skills | head
# 쓸 만한 skill은 .claude/skills/로 복사하고 third_party/ecc/README.md 목록에 추가.
set -euo pipefail
cd "$(dirname "$0")/.."
DEST=third_party/ecc/repo
if [ -d "$DEST/.git" ]; then
  git -C "$DEST" pull --ff-only
else
  git clone --depth 1 https://github.com/affaan-m/ECC "$DEST"
fi
echo "skills: $(ls "$DEST/skills" | wc -l), agents: $(ls "$DEST/agents" | wc -l)"
