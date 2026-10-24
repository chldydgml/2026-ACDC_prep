# ECC에서 가져온 것

출처: https://github.com/affaan-m/ECC (everything-claude-code), MIT License(`LICENSE`).
기준 커밋: `COMMIT` 파일 참고.

통째로 설치하지 않고 필요한 것만 복사했다.

| 복사한 것 | 위치 | 이유 | 수정 |
|---|---|---|---|
| `skills/pytorch-patterns` | `.claude/skills/pytorch-patterns/` | 적대적 공격 코드의 모델 로딩·텐서 처리 | 없음 |
| `skills/python-patterns` | `.claude/skills/python-patterns/` | 풀이 스크립트 일반 | 없음 |
| `skills/docker-patterns` | `.claude/skills/docker-patterns/` | 인프라 융합 문제의 컨테이너 구조 이해 | ECC 자체 설치 하네스 섹션 삭제, description 수정 |
| `skills/kubernetes-patterns` | `.claude/skills/kubernetes-patterns/` | K8s RBAC·Secret·kubectl 구조 이해 | 없음 |
| `agents/security-reviewer.md` | `.claude/agents/security-reviewer.md` | 인프라 문제에서 소스/설정 리뷰 | 없음 |

검토했지만 안 가져온 것: `security-bounty-hunter`(실제 저장소 대상), `deep-research`/`exa-search`(유료 MCP 필요),
`agent-security-hardening`(본선 A&D 가드레일용 — 본선 준비 때 다시 검토), `mle-workflow`(프로덕션 MLOps).

전체 원본이 필요하면 `scripts/fetch_ecc.sh` → `third_party/ecc/repo/`(git 제외).
