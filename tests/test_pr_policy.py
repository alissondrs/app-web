"""Tests for the app-web PR topology policy and its CI wiring.

Covers:
- valid/invalid/empty/missing/malformed policy declarations;
- branch-pair evaluation (known and unknown bases, absent head/base, edge
  wildcard matches);
- YAML <=> inline Python parity inside `.github/workflows/pr-policy.yml`;
- security invariants of the `pr-policy` workflow;
- stability of the existing CI check names.
"""

import ast
import re
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate_pr_policy as policy_module

POLICY_PATH = ROOT / ".github" / "pr-policy.yml"
PR_POLICY_WORKFLOW = ROOT / ".github" / "workflows" / "pr-policy.yml"
BUILD_PUBLISH_WORKFLOW = ROOT / ".github" / "workflows" / "build-publish.yml"
CI_WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"

SNIPPET_RE = re.compile(r"python3\s+-\s*<<'PY'\n(.*?)\n[ \t]*PY", re.DOTALL)
RULES_RE = re.compile(r"RULES\s*=\s*(\[[^\]]*\])")

VALID_PAIRS = [
    ("pre-develop/ci-pr-policy", "develop"),
    ("pre-develop/anything/deep", "develop"),
    ("develop", "main"),
]

INVALID_PAIRS = [
    ("feature/x", "develop"),
    ("support/hotfix", "main"),
    ("pre-develop/x", "main"),
    ("pre-develop/x", "develop-extra"),
    ("develop", "develop"),
    ("develop", "main-extra"),
    ("main", "main"),
    ("pre-develop", "develop"),
    ("pre-develop/", "develop"),
    ("developfoo", "main"),
    (None, "develop"),
    ("pre-develop/ci-pr-policy", None),
    ("", "develop"),
    ("pre-develop/ci-pr-policy", ""),
]


def _valid_policy_text():
    return POLICY_PATH.read_text(encoding="utf-8")


def _inline_snippet():
    text = _workflow_text()
    match = SNIPPET_RE.search(text)
    if not match:
        raise AssertionError("inline python snippet not found in pr-policy workflow")
    return textwrap.dedent(match.group(1))


def _inline_module():
    namespace = {}
    exec(_inline_snippet(), namespace)
    return namespace


def _workflow_text():
    return PR_POLICY_WORKFLOW.read_text(encoding="utf-8")


def _run_cli(*args):
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_pr_policy.py"), *args],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )


class EvaluateTestCase(unittest.TestCase):
    def test_valid_pairs_are_accepted(self):
        for head, base in VALID_PAIRS:
            with self.subTest(pair=(head, base)):
                self.assertIsNone(policy_module.evaluate(head, base))

    def test_invalid_or_unknown_pairs_are_rejected(self):
        for head, base in INVALID_PAIRS:
            with self.subTest(pair=(head, base)):
                self.assertIsNotNone(policy_module.evaluate(head, base))

    def test_matches_beats_equal_matching_and_trailing_slash(self):
        self.assertIsNone(policy_module.evaluate("pre-develop/ci-pr-policy", "develop"))
        self.assertIsNotNone(policy_module.evaluate("pre-develop/", "develop"))
        self.assertIsNotNone(policy_module.evaluate("pre-develop", "develop"))
        self.assertIsNotNone(policy_module.evaluate("develop2", "main"))

    def test_unknown_base_is_denied_fail_closed(self):
        self.assertIsNotNone(policy_module.evaluate("pre-develop/x", "other"))
        self.assertIsNotNone(policy_module.evaluate("develop", "develop"))

    def test_unknown_base_is_denied_by_inline_logic(self):
        inline = _inline_module()
        for head, base in (
            ("pre-develop/x", "other"),
            ("feature/x", "develop"),
            ("develop", "develop"),
            ("develop", "main-extra"),
        ):
            with self.subTest(pair=(head, base)):
                self.assertIsNotNone(inline["evaluate"](head, base))

    def test_rules_are_non_empty(self):
        self.assertNotEqual(len(policy_module.RULES), 0)


class ParseAndValidateTestCase(unittest.TestCase):
    def test_repo_policy_is_valid(self):
        self.assertEqual(policy_module.validate(str(POLICY_PATH)), [])

    def test_missing_file_fails_closed(self):
        problems = policy_module.validate(str(ROOT / ".github" / "does-not-exist.yml"))
        self.assertTrue(problems)

    def test_empty_policy_fails(self):
        with tempfile.NamedTemporaryFile(
            "w", suffix=".yml", delete=False
        ) as handle:
            handle.write("")
            name = handle.name
        try:
            problems = policy_module.validate(name)
        finally:
            Path(name).unlink()
        self.assertTrue(problems)
        joined = "; ".join(problems)
        self.assertIn("rules", joined)

    def test_fail_closed_false_is_rejected(self):
        text = _valid_policy_text().replace("fail_closed: true", "fail_closed: false")
        with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False) as f:
            f.write(text)
            name = f.name
        try:
            problems = policy_module.validate(name)
        finally:
            Path(name).unlink()
        self.assertTrue(problems)

    def test_extra_rule_is_rejected(self):
        text = _valid_policy_text() + "\n  - from: feature/*\n    to: develop\n"
        with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False) as f:
            f.write(text)
            name = f.name
        try:
            problems = policy_module.validate(name)
        finally:
            Path(name).unlink()
        self.assertTrue(problems)
        self.assertTrue(any("unexpected rules" in p for p in problems))

    def test_missing_rule_is_rejected(self):
        text = _valid_policy_text().replace(
            '  - from: develop\n    to: main\n', ''
        )
        with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False) as f:
            f.write(text)
            name = f.name
        try:
            problems = policy_module.validate(name)
        finally:
            Path(name).unlink()
        self.assertTrue(problems)
        self.assertTrue(any("missing rules" in p for p in problems))

    def test_unknown_base_in_policy_is_rejected(self):
        text = _valid_policy_text().replace(
            "    to: main\n", "    to: prod\n", 1
        )
        with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False) as f:
            f.write(text)
            name = f.name
        try:
            problems = policy_module.validate(name)
        finally:
            Path(name).unlink()
        self.assertTrue(problems)

    def test_malformed_policy_is_rejected(self):
        malformed = [
            "version: 1\nfail_closed: true\nrules: nope\n",
            "version: 1\nfail_closed: true\nrules:\n  - from: x\n  - from: y\n    to: z\n",
            "version: 1\nfail_closed: true\nrules:\n  - from: x\n    to: y\n    to: z\n",
            "version: 1\nfail_closed: maybe\nrules:\n",
            "version: 1\nfail_closed: true\nunknown: 1\nrules:\n",
            "version: 1\nfail_closed: true\nrules:\n\t- from: x\n\t  to: y\n",
        ]
        for text in malformed:
            with self.subTest(policy=text):
                with tempfile.NamedTemporaryFile(
                    "w", suffix=".yml", delete=False
                ) as f:
                    f.write(text)
                    name = f.name
                try:
                    problems = policy_module.validate(name)
                finally:
                    Path(name).unlink()
                self.assertTrue(problems)

    def test_duplicate_keys_are_rejected(self):
        text = (
            "version: 1\nversion: 1\nfail_closed: true\n"
            "rules:\n  - from: pre-develop/*\n    to: develop\n"
            "  - from: develop\n    to: main\n"
        )
        with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False) as f:
            f.write(text)
            name = f.name
        try:
            problems = policy_module.validate(name)
        finally:
            Path(name).unlink()
        self.assertTrue(problems)


class CliTestCase(unittest.TestCase):
    def test_cli_accepts_repo_policy(self):
        result = _run_cli(str(POLICY_PATH))
        self.assertEqual(result.returncode, 0)
        self.assertIn("OK", result.stdout)

    def test_cli_fails_on_missing_policy(self):
        result = _run_cli(str(ROOT / ".github" / "missing-policy.yml"))
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(result.stderr)

    def test_cli_fails_on_empty_policy(self):
        with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False) as f:
            f.write("")
            name = f.name
        try:
            result = _run_cli(name)
        finally:
            Path(name).unlink()
        self.assertNotEqual(result.returncode, 0)

    def test_cli_uses_default_path(self):
        result = _run_cli()
        self.assertEqual(result.returncode, 0)


class ParityTestCase(unittest.TestCase):
    def test_inline_rules_equal_yaml_rules(self):
        namespace = _inline_module()
        inline_rules = namespace["RULES"]
        parsed = policy_module.parse_policy(_valid_policy_text())
        self.assertEqual(tuple(inline_rules), parsed.rules)
        self.assertEqual(tuple(inline_rules), policy_module.EXPECTED_RULES)

    def test_inline_and_module_agree_on_all_pairs(self):
        inline = _inline_module()
        branches = [
            "pre-develop/ci-pr-policy",
            "pre-develop/",
            "pre-develop",
            "develop",
            "develop2",
            "feature/x",
            "main",
            "",
            None,
        ]
        for head in branches:
            for base in branches:
                with self.subTest(pair=(head, base)):
                    self.assertEqual(
                        inline["evaluate"](head, base),
                        policy_module.evaluate(head, base),
                    )

    def test_inline_and_module_agree_on_allowed_destinations(self):
        inline = _inline_module()
        for head in ["pre-develop/x", "develop", "feature/x", None, ""]:
            with self.subTest(head=head):
                self.assertEqual(
                    inline["allowed_destinations"](head),
                    policy_module.allowed_destinations(head),
                )

    def test_rules_list_matches_monotonic_singleton_format(self):
        match = RULES_RE.search(_workflow_text())
        self.assertIsNotNone(match, "RULES must be a single-line literal")
        rules = ast.literal_eval(match.group(1))
        self.assertEqual(tuple(rules), policy_module.EXPECTED_RULES)


class WorkflowSecurityTestCase(unittest.TestCase):
    def _text(self):
        return _workflow_text()

    def test_no_uses_no_checkout_no_secrets_no_pip(self):
        text = self._text()
        for forbidden in (
            "uses:",
            "actions/checkout",
            "secrets.",
            "GITHUB_TOKEN",
            "pip",
            "setup-python",
            "workflow_dispatch",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, text)

    def test_trigger_is_only_pull_request_target(self):
        lines = [line.strip() for line in self._text().splitlines()]
        self.assertIn("pull_request_target:", lines)
        self.assertNotIn("pull_request:", lines)

    def test_trigger_observes_every_pr_without_base_branch_filter(self):
        text = self._text()
        self.assertNotIn("branches:", text)
        self.assertNotIn("- develop", text)
        self.assertNotIn("- main", text)

    def test_permissions_read_only_contents(self):
        text = self._text()
        self.assertIn("contents: read", text)
        self.assertNotIn("contents: write", text)

    def test_job_is_named_pr_policy(self):
        text = self._text()
        self.assertIn("  pr-policy:", text)
        self.assertIn("    name: pr-policy", text)

    def test_job_has_single_run_step(self):
        text = self._text()
        self.assertEqual(text.count("run: |"), 1)
        self.assertEqual(text.count("- name:"), 1)


class CiStabilityTestCase(unittest.TestCase):
    def test_job_names_and_ids_are_preserved(self):
        text = CI_WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("name: Test and static checks", text)
        self.assertIn("name: Build Docker image", text)
        self.assertIn("  test:", text)
        self.assertIn("  docker:", text)

    def test_ci_has_auditable_artifacts_with_short_retention(self):
        text = CI_WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("retention-days: 7", text)
        self.assertIn("upload-artifact@v4", text)
        self.assertNotIn("awk 1", text)
        self.assertIn("!cancelled()", text)

    def test_publish_workflow_is_untouched(self):
        text = BUILD_PUBLISH_WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("name: Build and publish image", text)
        self.assertNotIn("pr-policy", text)


if __name__ == "__main__":
    unittest.main()
