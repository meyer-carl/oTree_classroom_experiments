# Data And Export

## What To Preserve

- session config used for the run
- room assignment and participant labels
- identity mode used for the run
- app order and any manual instructor interventions
- random paying round, if one was selected
- notes about unmatched or timed-out participants

## Recommended Export Review

1. Confirm every app produced the expected fields.
2. Check whether the debrief-relevant fields are present.
3. Verify that helper apps like `survey` and `payment_info` were included only when intended.
4. Keep a copy of the export notes with the class record.

## Quarter Summary Workflow

For tracked pseudonymous classes:

1. Save each class export in one folder.
2. Keep the session config name and class date in the filename.
3. Aggregate the quarter totals with the helper script.

Paste this into Terminal:

```bash
python scripts/build_quarter_earnings.py \
  exports/ \
  --output dist/quarter_earnings.csv
```

What this command does:

- reads every CSV export in `exports/`
- groups rows by participant label
- sums the detected payoff column
- writes one summary CSV to `dist/quarter_earnings.csv`

What `--output` means:

- it tells the script where to save the final summary file

## Operational Guidance

- treat `db.sqlite3` as local state, not as the source of truth
- export before any destructive cleanup
- keep the private mapping from real names to pseudonymous labels outside this repo
