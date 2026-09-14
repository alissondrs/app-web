# AGENTS.md — app-web

Operating rules for AI agents and automation working in this repository.

## Project

`app-web` is an educational Flask CRUD API (Python 3.10) backed by MySQL,
packaged with Docker and deployed to Kubernetes. CI runs on GitHub Actions;
image publishing is handled by a separate workflow.

- Entrypoint: `src/app/app.py` → `create_app()` in `src/app/webapp/`.
- Tests: `tests/` (stdlib `unittest`).
- Automation contract: `ci-project.yaml`.
- Local stack: `docker-compose/`. Cluster manifests: `k8s/kubernetes/` and
  `deploy/kubernetes/`. Harness contract: `deploy/harness/README.md`.

## Guarded files

Do not modify these unless a demonstrated, in-scope need appears and it is
explicitly authorized:

- `src/app/requirements.txt` (single dependency file, no multi-file split);
- `Dockerfile`;
- `.github/workflows/build-publish.yml`.

## Commands

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r src/app/requirements.txt

python -m unittest discover -s tests -p 'test_*.py'   # tests
ruff check src tests --select F                        # lint (CI)
pip-audit -r src/app/requirements.txt                  # dependency audit
docker build . --tag alissondrs/app-web:local          # image build

python scripts/validate_pr_policy.py                   # validate PR policy
```

Never install extra tooling as part of a task just to make a check pass;
record missing tools instead.

## Branch topology (fail-closed)

`.github/pr-policy.yml` declares the **only** allowed transitions:

- `pre-develop/* → develop`
- `develop → main`

Everything else is denied. The `pr-policy` check in
`.github/workflows/pr-policy.yml` runs on `pull_request_target` for **every**
pull request (no base-branch filter) with `permissions: contents: read`. It
reads only the event `head`/`base` refs and runs trusted inline logic; it never
checks out the PR head, installs dependencies, uses third-party actions, or
consumes secrets. Only the two pairs above pass; any missing, malformed,
unknown, or inconclusive condition—including a base outside the two allowed
pairs—fails the check. Keep the inline rules and the YAML in parity;
`tests/test_pr_policy.py` enforces this.

## CI (stable checks)

- `Test and static checks` (job `test`): tests, lint, dependency audit.
- `Build Docker image` (job `docker`): image build plus secret scan.

Do not rename these jobs or check names. CI runs fail-closed: a failing test,
lint, audit, build, or secret scan must fail the run. CI uploads short-retention
(`7` days) auditable evidence artifacts that must not contain secrets.

## Pre-develop workflow

1. Work only in an isolated worktree created from a refreshed `origin/develop`.
   Never stash, reset, clean, or copy the pre-existing worktree.
2. Implement the scoped change on `pre-develop/<topic>`.
3. Keep local tests green (`python -m unittest discover -s tests -p 'test_*.py'`),
   validate the policy (`python scripts/validate_pr_policy.py`), and confirm a
   clean worktree with zero drift behind `origin/develop`.
4. Require a final review PASS before any external write.

## Authorization after PASS

Only after a final review PASS, mandatory local tests green, a valid
`pre-develop/*` branch, a clean isolated worktree, and zero drift behind
`origin/develop`, an agent is authorized to:

- push the branch, and
- open or update a **draft** pull request (`pre-develop/* → develop`), and
- monitor CI, responding fail-closed.

An agent is **never** authorized under this policy to:

- mark the PR ready for review;
- approve the PR;
- enable auto-merge;
- merge;
- change branch protection or required checks.

## Bootstrap (default branch = `main`)

1. Merge the policy change into `develop` without requiring `pr-policy`.
2. Promote `develop` to the default branch `main`.
3. Prove the flow with a pilot PR and observe the `pr-policy` check behavior.
4. Only then, in a separately authorized change, make `pr-policy` a required
   check.

## Security

This project is educational. Treat credentials as non-secret for the lab only;
never put secrets in artifacts, logs, commits, or versioned YAML. API has no
authentication and no HTTPS; do not enable it in production as-is.
