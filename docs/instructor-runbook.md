# Instructor Runbook

## Purpose

This runbook covers the minimum steps needed to launch, supervise, and close a live classroom session using the oTree experiment bundle.

## Before Class

1. If the machine is new, start with `docs/install-from-scratch.md`.
2. Confirm the desired session config exists in `settings.py`.
3. Choose how students will connect and read `docs/hosting-and-deployment.md` before the first real class.
4. Decide whether the session is `tracked_pseudonymous` or `fully_anonymous`.
5. Verify the relevant room file under `_rooms/` has the right participant labels.
6. Check `docs/headcount-and-fallbacks.md` before committing to a multiplayer app.
7. Decide whether the class will use strategy-method variants for ultimatum, trust, or centipede.
8. If the class needs surveys or payment instructions, include `survey` and `payment_info` in the flow.
9. Run `./scripts/verify_high_coverage.sh` before sharing the repo or using a changed app in class.

## Bootstrap

- Run `./scripts/bootstrap.sh` to create the project-local `.venv`.
- Install or refresh project dependencies through that local environment.
- Verify that the interpreter resolves the expected `otree` package.
- Use the verification scripts as written; they intentionally run against the repo-local `.venv` rather than any external Python on `PATH`.
- Confirm the admin password is set if the class will use the admin interface.
- Decide whether you will use Heroku or ngrok before you invite students.
- Treat a missing or stale `db.sqlite3` as a normal local reset condition.
- Run `./scripts/build_instructor_pdfs.sh` if you want printable handouts or a combined instructor packet.

## Launch Checklist

- Start the server.
- Open the admin interface.
- Create the session using the intended room or demo path.
- Confirm the app order matches the teaching plan.
- Load one browser as a test participant before bringing in the class.
- Confirm the final headcount still matches the app’s compatibility rule before launching.

## Manual Release Gate

- Create one bundled session such as `survey_payment` or a classroom bundle that includes `survey` and `payment_info`.
- Run one odd-headcount strategy-method app.
- Run one large-group market app.
- Confirm participant labels or room flow behave as intended.
- Export the data and verify that the output fields are interpretable.

## During Class

- Keep one browser open on the admin page to monitor progress.
- Watch for incomplete groups and unmatched participants.
- If a student arrives late, check the headcount matrix before adding them to a running session.
- If a student opens the wrong link or refreshes repeatedly, inspect the admin page before assigning them a new seat.
- Pause between apps long enough to debrief the behavior, not just the outcome.
- If a timed app is used, announce the timing rule before the timer starts.

## After Class

- Export data before making changes to the database.
- Save any notes about unusual behavior, odd headcounts, or browser issues.
- Reset the room assignment if the next class needs a different participant pool.
- If the session used tracked pseudonymous labels, merge exports later with `python scripts/build_quarter_earnings.py`.
- Record any curriculum gaps in `docs/extension-roadmap.md` or your private teaching notes.

## Minimum Instructor Questions To Answer

- Which app is being used?
- How many participants are required?
- What happens when the room is short on players?
- What should students learn from the result?
- Which export fields matter afterward?
