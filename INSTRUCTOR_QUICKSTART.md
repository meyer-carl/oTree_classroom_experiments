# Instructor Quick Start

This is the shortest path from a fresh copy of the project to a live classroom session.

If you are comfortable with GitHub, you can use the repository directly. If not, download the packaged release ZIP and work from that folder instead.

## Prerequisites

- Python 3.12 available as `python3.12`
- A terminal
- A web browser for the instructor/admin page
- If you are starting from a blank computer, first read [docs/install-from-scratch.md](docs/install-from-scratch.md).

## First Setup

1. From the project root, run `./scripts/bootstrap.sh`.
2. Run `./scripts/verify_high_coverage.sh`.
3. If you want printable handouts or a combined instructor packet, run `./scripts/build_instructor_pdfs.sh`.
4. Set an admin password before launching oTree:

```bash
export OTREE_ADMIN_PASSWORD='choose-a-strong-password'
```

## Choose How Students Will Connect

- Local `otree devserver` is only local until you choose a public hosting option.
- Before the first real class, read [docs/hosting-and-deployment.md](docs/hosting-and-deployment.md).
- Default managed option: `Heroku`
- Free classroom option: `ngrok`
- Advanced long-term option: departmental `Ubuntu/Linux server`

## First Launch

1. Start with a live demo instead of a full class:

```bash
source .venv/bin/activate
otree devserver
```

2. Open the local oTree URL in a browser.
3. Log in as `admin`.
4. Create one session using `live_demo` before inviting students.

## Identity Mode

- For real classes, prefer stable pseudonymous labels such as `ECON101_001`.
- Generate or refresh a room-label file with:

```bash
python scripts/generate_room_labels.py --prefix ECON101 --count 40 --output _rooms/econ101.txt --force
```

- Use `live_demo` only when you want fully anonymous participation or a quick demo.

## What To Read Next

- [README.md](README.md)
- [docs/install-from-scratch.md](docs/install-from-scratch.md)
- [docs/classroom-readiness.md](docs/classroom-readiness.md)
- [docs/hosting-and-deployment.md](docs/hosting-and-deployment.md)
- [docs/identity-and-grading.md](docs/identity-and-grading.md)
- [docs/instructor-runbook.md](docs/instructor-runbook.md)
- [docs/experiment-catalog.md](docs/experiment-catalog.md)
- [docs/headcount-and-fallbacks.md](docs/headcount-and-fallbacks.md)
- [docs/classroom-playbooks.md](docs/classroom-playbooks.md)
- [docs/data-and-export.md](docs/data-and-export.md)

## Pre-Class Checklist

- Verify the intended session config exists in `settings.py`.
- Confirm the room file under `_rooms/` matches the participant-label plan.
- Decide between `tracked_pseudonymous` and `fully_anonymous` mode before class.
- Run `./scripts/verify_high_coverage.sh` after any local change.
- Test the first app with one instructor browser before class starts.
- Check `docs/headcount-and-fallbacks.md` before any multiplayer session.
- Decide in advance how you will handle odd headcounts for multiplayer sessions.

## Post-Class Checklist

- Export data before deleting or replacing `db.sqlite3`.
- Save the session config name, room name, and class date with the export.
- Note any unmatched participants, timeouts, or manual interventions.
- If you are using tracked labels, aggregate exports later with `python scripts/build_quarter_earnings.py`.

## Local Files To Keep Private Or Disposable

- `.venv/`: local Python environment, do not share.
- `db.sqlite3`: local session state, export data before resetting it.
- `dist/`: generated share packages, rebuild as needed.

## If Something Looks Wrong

- If imports fail unexpectedly, make sure you are running commands from the project root and that `./scripts/bootstrap.sh` completed successfully.
- If a session stalls, check the wait-page and unmatched guidance in `docs/troubleshooting.md`.
- If you need a release-level confidence check, run `./scripts/verify_full.sh`.
