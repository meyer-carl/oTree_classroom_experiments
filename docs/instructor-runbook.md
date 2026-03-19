# Instructor Runbook

## Purpose

This runbook covers the minimum steps needed to launch, supervise, and close a live classroom session using the oTree experiment bundle.

## Before Class

1. Confirm the Python environment is available and the project dependencies are installed.
2. Confirm the desired session config exists in `settings.py`.
3. Verify the relevant room file under `_rooms/` has the right participant labels.
4. Decide whether the class will use strategy-method variants for ultimatum, trust, or centipede.
5. If the class needs surveys or payment instructions, include `survey` and `payment_info` in the flow.
6. If imports behave strangely, check `docs/project/environment.md` for the local shadowing trap before changing code.

## Bootstrap

- Create or activate the local Python environment.
- Install the project dependencies from `requirements.txt`.
- Verify that the interpreter resolves the expected `otree` package.
- Confirm the admin password is set if the class will use the admin interface.
- Treat a missing or stale `db.sqlite3` as a normal local reset condition.

## Launch Checklist

- Start the server.
- Open the admin interface.
- Create the session using the intended room or demo path.
- Confirm the app order matches the teaching plan.
- Load one browser as a test participant before bringing in the class.

## During Class

- Keep one browser open on the admin page to monitor progress.
- Watch for incomplete groups and unmatched participants.
- Pause between apps long enough to debrief the behavior, not just the outcome.
- If a timed app is used, announce the timing rule before the timer starts.

## After Class

- Export data before making changes to the database.
- Save any notes about unusual behavior, odd headcounts, or browser issues.
- Reset the room assignment if the next class needs a different participant pool.
- Record any curriculum gaps in `docs/project/extension-backlog.md`.

## Minimum Instructor Questions To Answer

- Which app is being used?
- How many participants are required?
- What happens when the room is short on players?
- What should students learn from the result?
- Which export fields matter afterward?
