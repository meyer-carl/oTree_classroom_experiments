# Data and Export

## What To Preserve

- Session config used for the run.
- Room assignment and participant labels.
- Identity mode used for the run (`tracked_pseudonymous` or `fully_anonymous`).
- App order and any manual instructor interventions.
- Random paying round, if one was selected.
- Any notes about unmatched or timed-out participants.

## Recommended Export Review

1. Confirm every app produced the expected participant, group, and session fields.
2. Check whether the debrief-relevant fields are present.
3. Verify that shared helper apps like `survey` and `payment_info` are included only when intended.
4. Keep a copy of the export notes with the class record.

## Operational Guidance

- Treat `db.sqlite3` as local state, not a source of truth.
- Export before any destructive cleanup.
- If an instructor needs a handoff package, include the session config name, room name, and the live-class date.
- Keep the private mapping from real names to pseudonymous labels outside this repo.

## Quarter Summary Workflow

For tracked pseudonymous classes:

1. Save each class export in one folder.
2. Keep the session config name and class date in the filename.
3. Aggregate the quarter totals with:

```bash
python scripts/build_quarter_earnings.py exports/ --output dist/quarter_earnings.csv
```

4. Review the output before moving anything into a gradebook.

## Data Fields Worth Watching

- Allocation or contribution fields for bargaining and public goods.
- Bids, asks, and clearing prices for market apps.
- Random paying-round metadata for repeated games.
- Result-summary fields used in post-game discussion.
