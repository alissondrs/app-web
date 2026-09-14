# CI/CD — app-web

This document describes the continuous integration and delivery flow for
`app-web`, the security model of the pull request policy check, the stable
check names, the CI evidence artifacts, the local commands, and the bootstrap
order for enabling the policy.

## Flow

Pull requests are only allowed along the repository topology declared in
`.github/pr-policy.yml`:

- `pre-develop/* → develop`
- `develop → main`

Every other combination is denied. The `pr-policy` check enforces this before
code review and merge.

The image delivery flow is:

1. A PR into `develop` runs `.github/workflows/ci.yml` (tests, lint, dependency
   audit, Docker build, secret scan).
2. After merge into `develop`, `.github/workflows/build-publish.yml` publishes
   an immutable `develop-sha-*` image and uploads deployment metadata.
3. Promotion to production requires a second PR `develop → main`; only after
   that merge is a `prod-sha-*` image published.
4. The Harness CD contract consumes only immutable image tags. See
   `deploy/harness/README.md` and `deploy/kubernetes/README.md`.

## PR policy check (security model)

`.github/workflows/pr-policy.yml` defines a single job named `pr-policy`, which
is the check name surfaced on pull requests.

- Trigger: `pull_request_target` on **every** pull request (no base-branch
  filter), so PRs targeting any base—including unknown bases—go through the
  check and are denied unless they match one of the two allowed pairs.
- Permissions: `contents: read` only.
- It reads only the event payload at `GITHUB_EVENT_PATH` and extracts the
  `pull_request.head.ref` and `pull_request.base.ref` values.
- It never checks out the pull request head, installs dependencies, uses
  third-party actions, consumes secrets, or executes head code.
- It is fail-closed: absent or empty head/base, an unknown source, a base that
  is not allowed for the source, or any inconclusive evaluation fails the job.

`.github/pr-policy.yml` is the deterministic local declaration of the same
rules. `scripts/validate_pr_policy.py` parses it with a strict stdlib parser
and fails closed on missing, empty, malformed, duplicate, unknown, or
unexpected content. `tests/test_pr_policy.py` enforces parity between the YAML
declaration and the inline workflow logic, and asserts the security invariants
above.

## Stable checks

The following job names must not change; they are the required check names:

- `Test and static checks` (job `test`): `unittest`, `ruff --select F`,
  `pip-audit`.
- `Build Docker image` (job `docker`): Docker build plus `gitleaks` secret
  scan.

CI is fail-closed. A failing test, lint, audit, build, or secret scan fails the
run.

## Artifacts and retention

CI uploads short-retention (`retention-days: 7`) auditable evidence:

- `ci-evidence-test-<sha>`: the CI evidence summary and the captured
  `unittest` output.
- `ci-evidence-docker-<sha>`: the CI evidence summary for the image build.

Evidence steps run with `if: ${{ !cancelled() }}` so a failing run still
produces its evidence, and the secret scan runs with `if: ${{ always() }}`.
Artifacts must never contain secrets. `build-publish.yml` separately uploads
`image-metadata-<sha>` for `7` days.

## Commands

```bash
# Local tests
python -m unittest discover -s tests -p 'test_*.py'

# Lint and dependency audit (CI parity)
ruff check src tests --select F
pip-audit -r src/app/requirements.txt

# Validate the PR topology policy (fail-closed)
python scripts/validate_pr_policy.py

# Image build
docker build . --tag alissondrs/app-web:local
```

A deployment test command is also declared in `ci-project.yaml`
(`test_command`, `lint_command`, `dependency_audit_command`).

## Bootstrap

The default branch is `main`. To activate the policy safely:

1. Merge the policy change into `develop` **without** requiring `pr-policy`.
2. Promote `develop` to the default branch `main`.
3. Prove the flow with a pilot PR and observe the `pr-policy` check behavior.
4. Only then, in a separately authorized change, make `pr-policy` a required
   check.

Making `pr-policy` required before step 4 can deadlock the repository, because
the check only understands `pre-develop/* → develop` and `develop → main`.

## Limits and authorization

An agent working under this policy may, only after a final review PASS,
mandatory local tests green, a valid `pre-develop/*` branch, a clean isolated
worktree, and zero drift behind `origin/develop`:

- push the branch; and
- open or update a **draft** PR (`pre-develop/* → develop`); and
- monitor CI, responding fail-closed.

An agent is never authorized to mark a PR ready, approve it, enable
auto-merge, merge it, or change branch protection and required checks.
Bootstrap merges, pilot activation, and required-check changes are separate,
explicitly authorized gates.
