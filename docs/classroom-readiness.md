# Classroom Readiness

## What This Document Is For

This is the non-technical operating note for actually running these experiments with real students in a live class.

## Before You Start

- If this is a new machine, finish `docs/install-from-scratch.md` before doing anything else.
- Choose `tracked_pseudonymous` or `fully_anonymous` mode before class.
- If you want quarter-long earnings, use stable pseudonymous labels and a labeled room.
- If you want anonymity, use the unlabeled room and accept that quarter-long grading is not built in.
- Check the headcount matrix before you choose the app, not after students are already seated.

## Secure Room URLs

- Use secure labeled room URLs for real classes.
- Share the room links or labels before class starts.
- If students must type labels manually, have one spare browser open so you can test the room flow yourself first.

## Hosting Reliability In Class

- `Heroku` reduces dependence on the instructor laptop because the class connects to a hosted public app.
- `ngrok` can work well for small classes, but it requires the instructor machine to stay awake, connected, and running for the entire session.
- No matter which option you use, run one demo session before class and test the student link from a second device.

## Session Naming

Use a simple naming convention outside the app when you save exports and notes:

- `COURSE-YYYYMMDD-session_config`
- example: `ECON101-20260407-trust_with_survey`

Keep the same convention in your export filenames and teaching notes.

## Reserve Browser Policy

- Keep one or two reserve browsers available in the room.
- Use them for no-shows, frozen devices, or late replacements.
- This is especially important for apps that require exact multiples of `3`, `4`, or `8`.

## Late Arrivals

- Before session creation: safe if seats are still open.
- After session creation but before substantive play: only sometimes safe, and mainly for solo or ungrouped apps.
- After play has started: usually unsafe for multiplayer apps.

If a student arrives late:

1. Check the headcount matrix.
2. If the app is not late-arrival safe, do not improvise a new final group.
3. Use an observer/debrief role or hold the student for the next app.

## Wrong Link, Duplicate Link, and Refresh Problems

- If a student opens the wrong room, move them before creating the session if possible.
- In labeled rooms, duplicated start links are less dangerous because the label should map them back to the same participant.
- In anonymous rooms, duplicate participation risk is higher. Watch the room page before launching.
- If a student refreshes their browser, first check the admin page before reassigning them to a new seat.

## What To Write Down During Class

Keep a short log with:

- course and date
- session config name
- room name
- identity mode
- actual headcount
- any unmatched participants
- timeouts
- lost browsers
- manual replacements
- anything you had to explain twice because the interface was confusing

## What To Export Immediately After Class

- the oTree export
- the session config name
- the room name
- the class date
- the manual intervention log

If you are using tracked pseudonymous labels, keep exports in one folder so you can later run:

```bash
python scripts/build_quarter_earnings.py exports/ --output dist/quarter_earnings.csv
```

## Realistic Failure Modes To Anticipate

- one student is absent and the final group cannot form
- a browser freezes on a wait page
- a student joins twice from two tabs
- a student joins the wrong room
- a market app launches with the wrong headcount
- a timed app starts before students understand the rule

Build your classroom routine so you can recover from those without rewriting the lesson on the fly.

## Printable Release Checklist

- [ ] Correct room selected
- [ ] Correct identity mode selected
- [ ] Headcount multiple checked against the matrix
- [ ] Odd-headcount fallback chosen in advance
- [ ] Reserve browser available
- [ ] `OTREE_ADMIN_PASSWORD` set
- [ ] Session config and class date written down
- [ ] Export folder decided before class starts
- [ ] First participant flow tested before admitting the whole class
