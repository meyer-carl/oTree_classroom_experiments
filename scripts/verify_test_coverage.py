#!/usr/bin/env python3
from __future__ import annotations

from session_suites import ROOT, SUITE_ORDER, bundled_session_names, suite_sessions, validate_suite_assignments


def app_names():
    return sorted(
        path.name
        for path in ROOT.iterdir()
        if path.is_dir() and (path / "__init__.py").exists()
    )


def main() -> int:
    problems = list(validate_suite_assignments())

    for app_name in app_names():
        tests_path = ROOT / app_name / "tests.py"
        if not tests_path.exists():
            problems.append(f"{app_name}: missing tests.py")

    covered_sessions = set()
    for suite_name in SUITE_ORDER:
        covered_sessions.update(suite_sessions(suite_name))

    for session_name in bundled_session_names():
        if session_name not in covered_sessions:
            problems.append(f"{session_name}: bundled session missing from all suites")

    if problems:
        for problem in problems:
            print(problem)
        return 1

    print(
        f"Verified {len(app_names())} apps, {len(covered_sessions)} covered session configs, "
        f"and {len(bundled_session_names())} bundled configs."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
