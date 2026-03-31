# Contributor Guide

## Scope

This repository is optimized for teaching use. Code changes should preserve classroom reliability first and elegance second.

## Working Rules

- Keep session names stable unless there is a strong reason to change them.
- Add a test when you change payoff logic, grouping logic, or unmatched handling.
- Update the instructor docs whenever a classroom workflow changes.
- Prefer shared helpers over copied page logic.
- Check `docs/project/environment.md` before treating import issues as app bugs.
- Assign every new session config to `smoke`, `high`, or `full` immediately.

## Suggested Workflow

1. Read the relevant app and its tests.
2. Check the context pack in `docs/project/`.
3. Make the smallest behavioral change needed.
4. Add or update bot coverage.
5. Run `./scripts/bootstrap.sh` if the project-local `.venv` is missing, then use `./scripts/verify.sh` for local work and `./scripts/verify_high_coverage.sh` before handing work off.
6. Update the operator docs if the change affects instructors.

## What Good Looks Like

- A new instructor can run the app without reading source code.
- A reviewer can see the intended behavior from docs and tests.
- The classroom failure mode is documented before it happens live.
