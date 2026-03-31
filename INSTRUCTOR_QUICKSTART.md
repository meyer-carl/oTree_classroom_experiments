# Instructor Quick Start

This is the shortest path from a fresh copy of the project to a live classroom session.

## Prerequisites

- Python 3.12 available as `python3.12`
- A terminal
- A web browser for the instructor/admin page

## First Setup

1. From the project root, run `./scripts/bootstrap.sh`.
2. Run `./scripts/verify_high_coverage.sh`.
3. Set an admin password before launching oTree:

```bash
export OTREE_ADMIN_PASSWORD='choose-a-strong-password'
```

## First Launch

1. Start with a live demo instead of a full class:

```bash
source .venv/bin/activate
otree devserver
```

2. Open the local oTree URL in a browser.
3. Log in as `admin`.
4. Create one session using `live_demo` before inviting students.

## What To Read Next

- [README.md](/Users/carl/Documents/Teaching/oTree_classroom_experiments/README.md)
- [docs/instructor-runbook.md](/Users/carl/Documents/Teaching/oTree_classroom_experiments/docs/instructor-runbook.md)
- [docs/experiment-catalog.md](/Users/carl/Documents/Teaching/oTree_classroom_experiments/docs/experiment-catalog.md)
- [docs/classroom-playbooks.md](/Users/carl/Documents/Teaching/oTree_classroom_experiments/docs/classroom-playbooks.md)
- [docs/data-and-export.md](/Users/carl/Documents/Teaching/oTree_classroom_experiments/docs/data-and-export.md)

## Pre-Class Checklist

- Verify the intended session config exists in `settings.py`.
- Confirm the room file under `_rooms/` matches the participant-label plan.
- Run `./scripts/verify_high_coverage.sh` after any local change.
- Test the first app with one instructor browser before class starts.
- Decide in advance how you will handle odd headcounts for multiplayer sessions.

## Post-Class Checklist

- Export data before deleting or replacing `db.sqlite3`.
- Save the session config name, room name, and class date with the export.
- Note any unmatched participants, timeouts, or manual interventions.

## Local Files To Keep Private Or Disposable

- `.venv/`: local Python environment, do not share.
- `db.sqlite3`: local session state, export data before resetting it.
- `dist/`: generated share packages, rebuild as needed.

## If Something Looks Wrong

- If imports fail unexpectedly, make sure you are running commands from the project root and that `./scripts/bootstrap.sh` completed successfully.
- If a session stalls, check the wait-page and unmatched guidance in `docs/troubleshooting.md`.
- If you need a release-level confidence check, run `./scripts/verify_full.sh`.
