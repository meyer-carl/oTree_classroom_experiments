# Troubleshooting

Use this guide for live recovery during setup or class.

## Participant Is Unmatched

Likely cause:

- the final group is incomplete

What to do:

- check `01_instructor_pdfs/06_headcount_and_fallbacks.pdf` immediately
- if the app is a strategy-fallback app, use that path
- otherwise use a reserve browser, observer role, or different app

## Session Appears Stuck

Likely cause:

- a wait page is still waiting for another player

What to do:

- check whether a browser was abandoned
- confirm whether someone joined the wrong room or opened the link twice
- if the room is broken and the app is disposable, restart the session instead of guessing

## Strategy-Method Page Is Confusing

Likely cause:

- the class was not warned about the rule in advance

What to do:

- pause
- restate the rule out loud
- tell students exactly when their direct move matters and when their fallback answers matter

## Student Used The Wrong Link Or Refreshed Repeatedly

What to do:

- inspect the admin page before assigning a new seat
- in labeled rooms, confirm the student used the correct secure URL
- in anonymous rooms, watch for duplicate participation before continuing

## Market App Is One Trader Short

What to do:

- do not launch the market anyway
- use a reserve browser if you have one
- otherwise switch to a different app

## Export Looks Wrong Or Incomplete

What to do:

- confirm you exported the intended session
- save the session config name, room name, and date with the export
- if the issue persists, report the exact missing field to the maintainer who shared the package

## Good Recovery Habits

- do not delete `db.sqlite3` until the export is safe
- record odd headcounts, timeouts, and manual seat changes
- if a browser is lost mid-class, decide whether to wait, replace, or skip based on the app’s logic rather than improvising silently
