# Classroom Readiness

This is the non-technical operating note for real live classes.

## Before You Start

- If this is a new machine, finish `01_instructor_pdfs/01_install_from_scratch.pdf` first.
- Choose `tracked_pseudonymous` or `fully_anonymous` before class.
- If you want quarter-long earnings, use stable pseudonymous labels and a labeled room.
- Check `01_instructor_pdfs/06_headcount_and_fallbacks.pdf` before you choose the app, not after students are seated.

## Hosting Reliability

- `Heroku` reduces dependence on the instructor laptop because students connect to a hosted app.
- `ngrok` can work well for small classes, but it requires the instructor machine to stay awake, connected, and running for the whole session.
- No matter which option you choose, run one demo session before class and test the student link from a second device.

## Session Naming

Use a simple naming convention outside the app when you save exports and notes:

- `COURSE-YYYYMMDD-session_config`
- example: `ECON101-20260407-trust_with_survey`

## Reserve Browser Policy

- Keep one or two reserve browsers available.
- Use them for no-shows, frozen devices, or last-minute replacements.
- This matters most for apps that still require exact multiples of `2`, `4`, or `8`.

## Late Arrivals

Before session creation:

- safe if seats are still open

After session creation but before substantive play:

- sometimes safe for solo or odd-count-resilient apps

After play has started:

- usually unsafe for multiplayer apps

If a student arrives late:

1. check the headcount guide
2. do not improvise a broken final group
3. use an observer/debrief role if needed

## Wrong Link, Duplicate Link, And Refresh Problems

- if a student opens the wrong room, fix it before launch if possible
- in labeled rooms, duplicate links are less dangerous because the label maps back to the same participant
- in anonymous rooms, duplicate participation risk is higher
- if a student refreshes, check the admin page before assigning a new seat

## What To Write Down During Class

- course and date
- session config name
- room name
- identity mode
- actual headcount
- unmatched participants
- timeouts
- lost browsers
- manual replacements
- any confusing interface moment you had to explain twice

## What To Export Immediately After Class

- the oTree export
- the session config name
- the room name
- the class date
- the manual intervention log

If you are using tracked labels, paste this into Terminal later to build the quarter summary:

```bash
python scripts/build_quarter_earnings.py \
  exports/ \
  --output dist/quarter_earnings.csv
```

## Printable Release Checklist

- [ ] correct room selected
- [ ] correct identity mode selected
- [ ] headcount rule checked
- [ ] fallback chosen in advance
- [ ] reserve browser available
- [ ] `OTREE_ADMIN_PASSWORD` set
- [ ] session config and class date written down
- [ ] export folder decided before class starts
- [ ] first participant flow tested before admitting the whole class
