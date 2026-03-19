---
name: otree-test-author
description: Author bot tests and invariant checks for oTree classroom experiments, especially branch-heavy or classroom-risk flows.
---

# oTree Test Author

Use this skill when adding or improving bot coverage in classroom experiments.

## Workflow

1. Read the app and its current tests.
2. Identify the happy path, alternate path, and guardrail path.
3. Add tests for incomplete groups, timeouts, or randomized state when relevant.
4. Keep assertions deterministic and tied to payoff or result invariants.
5. Update docs if the test reveals a live-class failure mode.

## Minimum Coverage

- Happy path.
- Alternate outcome or branch.
- Invalid input or submission guard.
- Multiplayer apps: incomplete-group behavior.
- Repeated-round apps: state persistence.

## Keep In Mind

- Prefer high-signal tests over exhaustive but brittle tests.
- Test the business rule, not the template text.
