# Instructor Runbook

This runbook covers the minimum steps needed to launch, supervise, and close a live classroom session.

## Before Class

1. If the machine is new, finish `01_instructor_pdfs/01_install_from_scratch.pdf`.
2. Read `01_instructor_pdfs/03_hosting_and_deployment.pdf` and decide how students will connect.
3. Decide whether the session will be `tracked_pseudonymous` or `fully_anonymous`.
4. Check `01_instructor_pdfs/06_headcount_and_fallbacks.pdf` before you commit to a multiplayer app.
5. Decide whether the class will use a legacy preset or one of the new flexible presets where available.
6. Run the broader automated check before class.

Paste this into Terminal:

```bash
./scripts/verify_high_coverage.sh
```

## Bootstrap

Paste this into Terminal from the project root:

```bash
./scripts/bootstrap.sh
```

This creates the project-local `.venv` and installs the project dependencies.

If you want the clickable docs site and the numbered PDFs locally, paste this into Terminal:

```bash
./scripts/build_instructor_pdfs.sh
./scripts/build_instructor_site.sh
```

## Launch Checklist

1. Start the server.

Paste this into Terminal:

```bash
source .venv/bin/activate
otree devserver
```

2. Open the admin interface.
3. Create the session using the intended room or demo path.
4. Confirm the app order matches the teaching plan.
5. Load one browser as a test participant before bringing in the class.
6. Confirm the final headcount still matches the chosen preset.

## Demo Run Walkthrough

Do this once before the first real class:

1. Start `otree devserver`.
2. Log in as `admin`.
3. Create a `live_demo` session.
4. Open the participant link in a second browser or private window.
5. Complete one short run.
6. Export the data once so you know where the export lives.

For official background, see the oTree room and server docs referenced in `03_hosting_and_deployment`.

## During Class

- Keep one browser open on the admin page to monitor progress.
- Watch for incomplete groups and unmatched participants.
- If a student arrives late, check `01_instructor_pdfs/06_headcount_and_fallbacks.pdf` before seating them.
- If a student opens the wrong link or refreshes repeatedly, inspect the admin page before assigning them a new seat.
- Pause long enough to debrief behavior, not just outcomes.

## After Class

1. Export data before making changes to `db.sqlite3`.
2. Save notes about unusual behavior, odd headcounts, or browser issues.
3. Reset the room assignment if the next class needs a different participant pool.

If you used tracked pseudonymous labels, paste this into Terminal later to build the quarter summary:

```bash
python scripts/build_quarter_earnings.py \
  exports/ \
  --output dist/quarter_earnings.csv
```

What this command does:

- reads the export CSVs in `exports/`
- groups rows by participant label
- writes one quarter summary CSV to `dist/quarter_earnings.csv`

## Minimum Questions To Answer Before Launch

- Which app or preset am I using?
- How many participants do I need?
- What happens if the room is short?
- What should students learn from the result?
- Which export fields matter afterward?
