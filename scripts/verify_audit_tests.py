#!/usr/bin/env python3
"""Lightweight sanity check for the audit-tests branch.

This script does not require a working oTree installation. It verifies that the
hardening test modules remain syntactically valid and still include the branch
coverage markers we added.
"""

from __future__ import annotations

import py_compile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / 'ab_ultimatum' / 'tests.py',
    ROOT / 'ac_trust' / 'tests.py',
    ROOT / 'af_centipede' / 'tests.py',
    ROOT / 'ak_market_supply_demand' / 'tests.py',
    ROOT / 'as_competitiveness' / 'tests.py',
    ROOT / 'ai_prisoner_mult_rd' / 'tests.py',
]

REQUIRED_MARKERS = {
    'ab_ultimatum/tests.py': ['cases =', 'SubmissionMustFail', 'StrategyResponse', 'Response'],
    'ac_trust/tests.py': ['cases =', 'SubmissionMustFail', 'StrategySendBack', 'SendBack'],
    'af_centipede/tests.py': ['cases =', 'SubmissionMustFail', 'StrategyDecision', 'Decision'],
    'ak_market_supply_demand/tests.py': ['cases =', 'SubmissionMustFail', 'num_trades', 'clearing_price'],
    'as_competitiveness/tests.py': ['cases =', 'SubmissionMustFail', 'Choice', 'Task'],
    'ai_prisoner_mult_rd/tests.py': ['cases =', 'SubmissionMustFail', 'mutual_cooperate', 'alternating'],
}


def main() -> int:
    problems: list[str] = []
    for path in TARGETS:
        try:
            py_compile.compile(str(path), doraise=True)
        except Exception as exc:
            problems.append(f'{path}: syntax check failed: {exc}')
            continue

        text = path.read_text()
        rel = path.relative_to(ROOT).as_posix()
        for marker in REQUIRED_MARKERS[rel]:
            if marker not in text:
                problems.append(f'{rel}: missing marker {marker!r}')

    if problems:
        for problem in problems:
            print(problem)
        return 1

    print(f'Checked {len(TARGETS)} files successfully.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
