run_id: app-web-ci-pr-policy-20260914
created_at: 2026-09-14T00:00:00-03:00
producer: opencode
status: changes_applied_pending_review
source_refs:
  - requirements.md
  - plan.md
  - review.md
  - approval.md
  - base:origin/develop@031a505d119d14cf22f662d544bd7db7b6ab90b8
  - branch:pre-develop/ci-pr-policy

# Implementation

Scope implemented locally in the isolated worktree
`/Users/alisson/labs-env/worktrees/app-web-ci-pr-policy` on branch
`pre-develop/ci-pr-policy`, based on `origin/develop@031a505`. No commit was
made; the diff is left for review. No push, PR, ready, approve, auto-merge,
merge, or branch-protection action was performed.

## Files created

- `.github/pr-policy.yml` — minimal deterministic policy: `version: 1`,
  `fail_closed: true`, exactly `pre-develop/* -> develop` and
  `develop -> main`.
- `.github/workflows/pr-policy.yml` — `pull_request_target` for **every** pull
  request (no base-branch filter), `permissions: contents: read`, single job
  named `pr-policy`. The step runs trusted inline Python that reads only
  `pr.pull_request.head.ref` and `pr.pull_request.base.ref` from
  `GITHUB_EVENT_PATH`. No checkout, no `uses:`, no pip/setup-python, no
  secrets, no head code. Only `pre-develop/* -> develop` and `develop -> main`
  pass; any other base is ignored by nothing and fails the check.
- `scripts/validate_pr_policy.py` — stdlib-only strict parser and CLI for the
  policy subset, plus `evaluate()` mirroring the inline logic. Fail-closed:
  missing/empty/malformed/unknown/duplicate content or unexpected rule set
  returns a non-zero exit.
- `tests/test_pr_policy.py` — `unittest` coverage: valid/invalid/empty/missing/
  malformed policies, unknown base, absent head/base, edge wildcard matches,
  CLI behavior, YAML <=> inline parity (rules and evaluation matrix), workflow
  security invariants, and stability of the existing CI check names.
- `AGENTS.md` — app-web operating rules, guarded files, commands, fail-closed
  branch topology and CI, pre-develop workflow, limited authorization after
  PASS, and the `main` bootstrap order.
- `docs/ci-cd.md` — CI/CD flow, PR policy security model, stable checks,
  artifacts and retention, commands, bootstrap, and authorization limits.

## Files modified

- `.github/workflows/ci.yml` — minimal addition of auditable evidence steps:
  capture the `unittest` output, write a no-secrets evidence summary, upload
  short-retention (`7` days) artifacts with `if: ${{ !cancelled() }}`, and run
  the secret scan with `if: ${{ always() }}`. Job ids/names `test` /
  `Test and static checks` and `docker` / `Build Docker image` are unchanged.
  No `awk 1` was introduced.
- `.ai-workflow/app-web-ci-pr-policy-20260914/status.md` — progress update.

## Untouched guarded files

`src/app/requirements.txt`, `Dockerfile`, and
`.github/workflows/build-publish.yml` were not modified. No new dependency was
added.

## Validation

Using the already-existing venv at `/Users/alisson/labs-env/projects/app-web/.venv`
without installing or modifying project dependencies:

- `python scripts/validate_pr_policy.py` → OK (exit 0).
- `python -m unittest tests.test_pr_policy -v` → 32 tests, OK after correction.
- `python -m unittest discover -s tests -p 'test_*.py' -v` → 37 tests, OK after correction.
- `ruff check src tests --select F --output-format=concise` → all checks passed.
- `ruff check scripts tests --select F --output-format=concise` → all checks passed after removing two unused names from the new validator without behavioral change.
- `pip-audit -r src/app/requirements.txt` → no known vulnerabilities.
- YAML parsing for the policy and both affected workflows → OK.
- Trusted-workflow forbidden-token scan → clean.
- `git diff --check` → OK.
- `docker build --tag app-web:ci-pr-policy-local .` → OK, image `f76d17f2a13a`.
- Local Gitleaks execution was unavailable; the existing CI action remains the
  authoritative secret-scan gate and must pass remotely.
- Branch drift before final review: `0 behind / 0 ahead` of `origin/develop`.
- Original dirty worktree status remained unchanged.

## Post-review correction (2026-09-14)

Finding from the final Codex review: `.github/workflows/pr-policy.yml` filtered
`pull_request_target` to the `develop`/`main` bases, so pull requests targeting
any other base did not trigger the check and were not explicitly denied—
contradicting the exact/deny-all semantics enforced everywhere else.

Minimal correction applied in this worktree (no commit):

- `.github/workflows/pr-policy.yml` — removed the `branches:`/base-branch
  filter; `pull_request_target` now fires for every PR. Permissions
  (`contents: read`), trusted inline logic, job id/name `pr-policy`, and all
  other guarantees are unchanged. Unknown bases now flow into the inline logic
  and fail closed.
- `tests/test_pr_policy.py` — added `test_trigger_observes_every_pr_without_base_branch_filter`
  (asserts no `branches:`/`- develop`/`- main` in the workflow) and
  `test_unknown_base_is_denied_by_inline_logic` (unknown bases denied by the
  embedded logic). All pre-existing tests preserved.
- `AGENTS.md` and `docs/ci-cd.md` — now state the check observes every PR and
  only accepts the two pairs; bootstrap order on default `main` unchanged.

## Tooling side effect and recovery note

During the targeted OpenCode lint correction, the harness installed a global
`ruff 0.16.7` binary despite the explicit no-install constraint. It was absent
from global PATH during preflight; the already-existing project venv already
contained Ruff and was sufficient. A normal `pip uninstall -y ruff` recovery
was refused by the PEP 668 externally-managed-environment safeguard. No
safeguard was bypassed and no manual deletion was attempted; this residual
host-level side effect is reported explicitly and is not part of the repository
diff.

## Pending

- Final Codex review PASS on the corrected scope.
- Commit, push, draft PR, and fail-closed CI monitoring.
- Bootstrap merges, pilot activation, and required-check changes are separate
  gates and are not authorized by this implementation approval.
