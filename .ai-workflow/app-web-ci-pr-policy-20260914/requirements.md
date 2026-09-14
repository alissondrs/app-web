run_id: app-web-ci-pr-policy-20260914
created_at: 2026-09-14T07:14:00-03:00
producer: copilot
status: approved
source_refs:
  - repo:app-web
  - base:origin/develop@031a505d119d14cf22f662d544bd7db7b6ab90b8
  - reference:spotfy-manager-v2/pre-develop/ci-pr-policy

# Requirements

1. Enforce PR topology `pre-develop/* -> develop` and `develop -> main`; deny all other combinations.
2. Add a stable `pr-policy` check using `pull_request_target`, `permissions: contents: read`, and trusted inline logic over event head/base only; no checkout, dependency installation, secrets, or execution of PR-head code.
3. Fail closed for missing/malformed policy, absent head/base, unknown base, invalid pair, or inconclusive evaluation.
4. Keep a deterministic local policy declaration and stdlib-compatible validator, with `unittest` parity/security tests and no new dependency.
5. Preserve existing CI behavior and required-check names `Test and static checks` and `Build Docker image`.
6. Keep the single `src/app/requirements.txt`; do not port the multi-requirements `awk 1` fix.
7. Add auditable CI evidence without secrets and document retention.
8. Permit push plus opening/updating a PR draft only after final review PASS, mandatory local tests green, valid branch, clean isolated worktree, and zero drift behind `origin/develop`; then monitor CI fail-closed.
9. Never mark ready, approve, enable auto-merge, merge, or alter branch protection under this authorization.
10. Document bootstrap: merge into develop without requiring `pr-policy`, promote develop to default branch main, prove a pilot PR, then separately authorize required-check changes.
11. Preserve the original dirty worktree completely; implementation occurs only in an isolated worktree from refreshed `origin/develop`.
12. Do not change Flask behavior, test framework, application dependencies, Dockerfile, or publishing workflow unless a demonstrated in-scope need appears.
