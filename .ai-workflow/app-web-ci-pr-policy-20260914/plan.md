run_id: app-web-ci-pr-policy-20260914
created_at: 2026-09-14T07:29:00-03:00
producer: codex
status: ready
source_refs:
  - requirements.md
  - base:origin/develop@031a505d119d14cf22f662d544bd7db7b6ab90b8

# Plan

1. Preserve the original `feat/app-web-structure-improvements` worktree; never stash, reset, clean, or copy its uncommitted files.
2. Refresh `origin/develop`, verify its remote SHA, and create isolated `pre-develop/ci-pr-policy` from that exact ref.
3. Add `.github/pr-policy.yml`, `.github/workflows/pr-policy.yml`, `scripts/validate_pr_policy.py`, and `tests/test_pr_policy.py` using stdlib/unittest.
4. Update `AGENTS.md` and add `docs/ci-cd.md`; minimally update `.github/workflows/ci.yml` for auditable artifacts while preserving check names.
5. Do not modify `src/app/requirements.txt`, `Dockerfile`, or `.github/workflows/build-publish.yml` by default.
6. Test valid/invalid/missing/malformed policy, exact parity with inline workflow logic, workflow safety, documentation consistency, current application tests, Ruff, pip-audit, Docker build, and secret scan where available.
7. Inspect scope and diff; require final Codex review PASS, clean worktree, valid branch, and no drift behind `origin/develop`.
8. Commit, push, and open/update a draft PR to develop; monitor CI. Never ready/approve/auto-merge/merge.
9. Leave bootstrap merges, pilot activation, and branch-protection changes for separately authorized gates.

# Rollback

Revert only this implementation's commits through normal PR history. Never use destructive reset/clean against the original worktree. Do not change branch protection as part of rollback without separate authorization.
