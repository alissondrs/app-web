#!/usr/bin/env python3
"""Strict stdlib validator for the app-web PR topology policy.

Parses `.github/pr-policy.yml` without external dependencies and validates that
it declares exactly `pre-develop/* -> develop` and `develop -> main` with
`fail_closed: true`. Anything else -- missing file, malformed YAML subset,
empty policy, unknown keys, missing/extra rules -- is a failure (exit != 0).

Usage:
    python scripts/validate_pr_policy.py [path]
"""

import re
import sys

DEFAULT_POLICY = ".github/pr-policy.yml"
EXPECTED_VERSION = 1
EXPECTED_RULES = (("pre-develop/*", "develop"), ("develop", "main"))

_KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$")
_RULE_FROM_RE = re.compile(r"^-\s+from:\s*(.+)$")
_RULE_TO_RE = re.compile(r"^to:\s*(.+)$")

# The inline logic embedded in `.github/workflows/pr-policy.yml` must stay in
# parity with this module (tests enforce it).
RULES = list(EXPECTED_RULES)


class PolicyParseError(Exception):
    pass


class Policy(object):
    def __init__(self, version, fail_closed, rules):
        self.version = version
        self.fail_closed = fail_closed
        self.rules = tuple(rules)


def _strip_quotes(value):
    value = value.strip()
    if len(value) >= 2 and value[0] in ("'", '"') and value[-1] == value[0]:
        head = value[0]
        if head not in value[1:-1]:
            return value[1:-1]
    return value


def _significant_lines(text):
    lines = []
    for number, raw in enumerate(text.splitlines(), start=1):
        content = raw.rstrip()
        if not content.strip():
            continue
        leading = content[: len(content) - len(content.lstrip(" "))]
        if "\t" in leading:
            raise PolicyParseError(
                "line %d: tabs are not allowed in indentation" % number
            )
        if content.lstrip().startswith("#"):
            continue
        lines.append((number, len(leading), content[len(leading):]))
    return lines


def parse_policy(text):
    version = None
    fail_closed = None
    rules = []
    saw_rules = False
    pending_from = None
    for number, indent, body in _significant_lines(text):
        if indent == 0 and not saw_rules:
            if pending_from is not None:
                raise PolicyParseError("line %d: incomplete rule" % number)
            match = _KEY_RE.match(body)
            if not match:
                raise PolicyParseError(
                    "line %d: expected 'key: value', got %r" % (number, body)
                )
            key, value = match.groups()
            if key == "version":
                if version is not None:
                    raise PolicyParseError("line %d: duplicate 'version'" % number)
                try:
                    version = int(value)
                except ValueError:
                    raise PolicyParseError(
                        "line %d: 'version' must be an integer" % number
                    )
            elif key == "fail_closed":
                if fail_closed is not None:
                    raise PolicyParseError("line %d: duplicate 'fail_closed'" % number)
                if value not in ("true", "false"):
                    raise PolicyParseError(
                        "line %d: 'fail_closed' must be true or false" % number
                    )
                fail_closed = value == "true"
            elif key == "rules":
                if saw_rules:
                    raise PolicyParseError("line %d: duplicate 'rules'" % number)
                saw_rules = True
            else:
                raise PolicyParseError("line %d: unknown key %r" % (number, key))
        elif saw_rules and indent == 2 and pending_from is None:
            match = _RULE_FROM_RE.match(body)
            if not match:
                raise PolicyParseError(
                    "line %d: expected '- from: <source>'" % number
                )
            pending_from = (number, _strip_quotes(match.group(1)))
        elif saw_rules and indent == 4 and pending_from is not None:
            match = _RULE_TO_RE.match(body)
            if not match:
                raise PolicyParseError(
                    "line %d: expected 'to: <destination>' for the rule starting at line %d"
                    % (number, pending_from[0])
                )
            rules.append((pending_from[1], _strip_quotes(match.group(1))))
            pending_from = None
        elif saw_rules and indent in (2, 4):
            raise PolicyParseError(
                "line %d: unexpected rule content %r" % (number, body)
            )
        else:
            raise PolicyParseError("line %d: unexpected content %r" % (number, body))
    if pending_from is not None:
        raise PolicyParseError(
            "rule starting at line %d has no 'to:' entry" % pending_from[0]
        )
    if not saw_rules:
        raise PolicyParseError("missing 'rules:' section")
    return Policy(
        version=version,
        fail_closed=fail_closed if fail_closed is not None else False,
        rules=rules,
    )


def _check(policy):
    problems = []
    if policy.version is None:
        problems.append("missing 'version'")
    elif policy.version != EXPECTED_VERSION:
        problems.append(
            "version must be %d, got %r" % (EXPECTED_VERSION, policy.version)
        )
    if policy.fail_closed is not True:
        problems.append("fail_closed must be true")
    rule_set = set(policy.rules)
    if len(rule_set) != len(policy.rules):
        problems.append("rules must not contain duplicates")
    expected_set = set(EXPECTED_RULES)
    if rule_set != expected_set:
        missing = sorted(expected_set - rule_set)
        extra = sorted(rule_set - expected_set)
        if missing:
            problems.append("missing rules: %s" % missing)
        if extra:
            problems.append("unexpected rules: %s" % extra)
    return problems


def validate(path):
    try:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
    except OSError as error:
        return ["cannot read policy: %s" % error]
    try:
        policy = parse_policy(text)
    except PolicyParseError as error:
        return [str(error)]
    return _check(policy)


def _matches(pattern, branch):
    if pattern.endswith("*"):
        prefix = pattern[:-1]
        return branch.startswith(prefix) and len(branch) > len(prefix)
    return pattern == branch


def allowed_destinations(head):
    if not head:
        return []
    return [destination for source, destination in RULES if _matches(source, head)]


def evaluate(head, base):
    if not head or not base:
        return "absent or empty head/base ref"
    destinations = allowed_destinations(head)
    if not destinations:
        return "head is not an allowed source: %s" % head
    if base not in destinations:
        return "base is not allowed for head: %s -> %s" % (head, base)
    return None


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if len(argv) > 1:
        print("usage: validate_pr_policy.py [path]", file=sys.stderr)
        return 2
    path = argv[0] if argv else DEFAULT_POLICY
    problems = validate(path)
    if problems:
        for problem in problems:
            print("FAIL %s: %s" % (path, problem), file=sys.stderr)
        return 1
    print(
        "OK %s: version=%d fail_closed=true rules=%s"
        % (path, EXPECTED_VERSION, sorted(EXPECTED_RULES))
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
