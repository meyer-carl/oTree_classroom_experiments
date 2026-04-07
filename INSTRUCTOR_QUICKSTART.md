# Instructor Quick Start

This is the shortest path from a fresh copy of the project to a live classroom session.

If you are using the release ZIP, open the numbered PDFs in `01_instructor_pdfs/` or the clickable website in `02_docs_site/index.html`. If you are browsing the repository directly, the same content is in the Markdown files listed below.

## Prerequisites

- Python `3.12` available as `python3.12`
- a terminal
- a web browser for the instructor/admin page

If the computer is blank, start with `01_instructor_pdfs/01_install_from_scratch.pdf` before doing anything else.

## First Setup

Paste this into Terminal from the project root:

```bash
./scripts/bootstrap.sh
./scripts/verify_high_coverage.sh
```

The first command creates a local `.venv` and installs the Python packages for this project, including oTree. The second command runs the broader automated check before you share the bundle or use it in class.

## Set The Admin Password

Paste this into Terminal and replace the example text with your own password:

```bash
export OTREE_ADMIN_PASSWORD='choose-a-strong-password'
```

You only need to choose the password text inside the quotes.

## Choose How Students Will Connect

- Local `otree devserver` is only local until you choose a public hosting option.
- Read the Hosting and Deployment guide before the first real class.
- Default managed option: `Heroku`
- Free classroom option: `ngrok`
- Advanced long-term option: departmental `Ubuntu/Linux server`

## Run One Demo First

Paste this into Terminal:

```bash
source .venv/bin/activate
otree devserver
```

This starts oTree on your own computer.

Then do this in your browser:

1. Open the local oTree URL shown in the terminal.
2. Log in as `admin`.
3. Create one `live_demo` session.
4. Open that session in a second browser or private window.
5. Click through one short run before inviting students.

## If You Use Tracked Labels

Paste this into Terminal to generate pseudonymous participant labels:

```bash
python scripts/generate_room_labels.py \
  --prefix ECON101 \
  --count 40 \
  --output _rooms/econ101.txt \
  --force
```

What the options mean:

- `--prefix ECON101`: the course code that appears before the number
- `--count 40`: create 40 labels
- `--output _rooms/econ101.txt`: write them into that room file
- `--force`: overwrite the file if it already exists

Use stable codes like `ECON101_001`, not student names.

## What To Read Next

Read these in this order:

1. `01_instructor_pdfs/01_install_from_scratch.pdf`
2. `01_instructor_pdfs/02_instructor_quickstart.pdf`
3. `01_instructor_pdfs/03_hosting_and_deployment.pdf`
4. `01_instructor_pdfs/04_identity_and_grading.pdf`
5. `01_instructor_pdfs/05_classroom_readiness.pdf`
6. `01_instructor_pdfs/06_experiment_catalog.pdf`
7. `01_instructor_pdfs/07_headcount_and_fallbacks.pdf`
8. `01_instructor_pdfs/08_instructor_runbook.pdf`
9. `01_instructor_pdfs/09_data_and_export.pdf`
10. `01_instructor_pdfs/10_troubleshooting.pdf`

If you prefer clickable docs inside the ZIP, open `02_docs_site/index.html`. It follows the same order.

## Pre-Class Checklist

- Confirm the intended session config exists in `settings.py`.
- Confirm the room file under `_rooms/` matches the participant-label plan.
- Decide between `tracked_pseudonymous` and `fully_anonymous` before class.
- Run `./scripts/verify_high_coverage.sh` after any local change.
- Test the first app with one instructor browser before class starts.
- Check `01_instructor_pdfs/06_headcount_and_fallbacks.pdf` and `01_instructor_pdfs/07_experiment_catalog.pdf` before any multiplayer session.

## Post-Class Checklist

- Export data before deleting or replacing `db.sqlite3`.
- Save the session config name, room name, and class date with the export.
- Note any unmatched participants, timeouts, or manual interventions.

Paste this into Terminal later if you used tracked labels:

```bash
python scripts/build_quarter_earnings.py \
  exports/ \
  --output dist/quarter_earnings.csv
```

What this command does:

- reads all export CSVs in `exports/`
- groups rows by participant label
- writes one summary CSV to `dist/quarter_earnings.csv`

## Local Files To Keep Private Or Disposable

- `.venv/`: local Python environment, do not share.
- `db.sqlite3`: local session state, export data before resetting it.
- `dist/`: generated release assets, rebuild as needed.
