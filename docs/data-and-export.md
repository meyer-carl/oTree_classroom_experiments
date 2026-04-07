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
3. Use the grading helper for grade-linked summaries.

Paste this into Terminal:

```bash
python scripts/build_grading_summary.py \
  exports/
```

What this command does:

- reads one or more `all_apps_wide.csv` exports in `exports/`
- groups rows by participant label and session
- writes `dist/grading/session_summary.csv`
- writes `dist/grading/quarter_summary.csv`

What the main outputs mean:

- `raw_earnings_points`: actual points earned in active opportunities
- `app_payoff_points`: oTree payoff after any classroom normalization
- `max_attainable_points`: best feasible payoff for the role and opportunity actually faced
- `attainment_fraction`: normalized attainment based on `raw_earnings_points / max_attainable_points`

Recommended instructor use:

- grade from `overall_attainment_fraction`
- use raw totals and percentiles only as a secondary diagnostic
- do not include anonymous sessions in grade-linked summaries

If you only need the old raw cumulative total, the legacy helper still works.

Paste this into Terminal:

```bash
python scripts/build_quarter_earnings.py \
  exports/ \
  --output dist/quarter_earnings.csv
```

## Operational Guidance

- treat `db.sqlite3` as local state, not as the source of truth
- export before any destructive cleanup
- keep the private mapping from real names to pseudonymous labels outside this repo
