#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from session_suites import ROOT, SUITE_ORDER, suite_sessions, validate_suite_assignments


def main() -> int:
    parser = argparse.ArgumentParser(description="Run an oTree bot suite.")
    parser.add_argument("suite", choices=SUITE_ORDER)
    parser.add_argument(
        "--list",
        action="store_true",
        help="Print the sessions in the suite and exit.",
    )
    args = parser.parse_args()

    problems = validate_suite_assignments()
    if problems:
        for problem in problems:
            print(problem)
        return 1

    sessions = suite_sessions(args.suite)
    if args.list:
        for session_name in sessions:
            print(session_name)
        return 0

    otree_cmd = Path(sys.executable).parent / "otree"
    if not otree_cmd.exists():
        print(
            "oTree CLI not found next to the active Python interpreter. "
            "Run ./scripts/bootstrap.sh to create the project-local .venv."
        )
        return 1

    failures = []
    for index, session_name in enumerate(sessions, start=1):
        print(f"[{index}/{len(sessions)}] Running otree test {session_name}", flush=True)
        result = subprocess.run([str(otree_cmd), "test", session_name], cwd=ROOT)
        if result.returncode != 0:
            failures.append(session_name)

    passed = len(sessions) - len(failures)
    print(
        f"Suite {args.suite}: {passed} passed, {len(failures)} failed, {len(sessions)} total."
    )
    if failures:
        print("Failed sessions: " + ", ".join(failures))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
