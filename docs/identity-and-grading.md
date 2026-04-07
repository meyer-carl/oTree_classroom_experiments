# Identity And Grading

Use one of these two modes on purpose. Do not switch casually in the middle of a quarter.

## Recommended Default: Tracked Pseudonymous

Use this mode for real classes where earnings may count toward participation or grades.

What students see:

- stable pseudonymous labels such as `ECON101_001`

Why this is the default:

- you can track participation across sessions
- you do not have to show student names in the classroom
- `payment_info` already displays `participant.label` when it exists

## Alternative: Fully Anonymous

Use this mode for one-off demos, guest lectures, or sessions where no quarter-long linkage is needed.

What students see:

- anonymous room entry or a one-time participant code

Tradeoff:

- this mode is not naturally compatible with grade-linked earnings unless you keep a separate offline alias map yourself

## Tracked Pseudonymous Workflow

Paste this into Terminal to generate stable participant labels:

```bash
python scripts/generate_room_labels.py \
  --prefix ECON101 \
  --count 40 \
  --output _rooms/econ101.txt \
  --force
```

What the options mean:

- `--prefix ECON101`: the course code that appears first
- `--count 40`: how many labels to create
- `--output _rooms/econ101.txt`: which room file to write
- `--force`: replace the existing file if it is already there

Then:

1. Share those labels or their secure room URLs with students.
2. Keep the real-name mapping outside this repo.
3. Reuse the same labels for the full quarter.

## Fully Anonymous Workflow

- Use the unlabeled `live_demo` room or another room with no participant label file.
- Do not promise quarter-long grade linkage from these sessions.
- If you later decide you need grading, create a separate offline alias map before the session begins.

## Secure Room URLs

- Labeled rooms should use secure URLs.
- Secure URLs stop students from typing a different `participant_label` to impersonate someone else.
- If you are running a tracked class, do not disable this protection for convenience.

## Payment Screen Behavior

`payment_info` displays:

- the participant label when the session uses tracked labels
- the anonymous oTree participant code when no label is present

## Quarter Earnings Workflow

After each class:

1. Export the session data.
2. Save the file with a clear course-date-app name.
3. Keep the session config name and room name with the export.

For grading, use the grading summary helper rather than the older raw-earnings helper.

Paste this into Terminal:

```bash
python scripts/build_grading_summary.py \
  exports/
```

What this command does:

- reads one or more `all_apps_wide.csv` exports from `exports/`
- requires participant labels by default
- writes a per-session summary to `dist/grading/session_summary.csv`
- writes a quarter summary to `dist/grading/quarter_summary.csv`

What the key grading columns mean:

- `raw_earnings_points`: the unnormalized points actually earned in active opportunities
- `app_payoff_points`: the oTree payoff total after any classroom normalization rule
- `max_attainable_points`: the best feasible payoff for the student's actual role and opportunity
- `attainment_fraction`: `raw_earnings_points / max_attainable_points`

Recommended grading basis:

- use `overall_attainment_fraction` from `dist/grading/quarter_summary.csv`
- treat raw earnings and raw-earnings percentiles as diagnostic information, not the grading rule
- do not use anonymous sessions for grade-linked summaries

Why this is fairer:

- sit-outs in role-balanced and pair-cycle presets count as zero opportunity, not as a missed earning chance
- students are compared against the best feasible payoff for the role they actually played
- flexible group sizes are handled using the actual session parameters and realized role opportunities

The older raw-only helper still exists for backward compatibility. If you only want simple cumulative earnings, paste this into Terminal:

```bash
python scripts/build_quarter_earnings.py \
  exports/ \
  --output dist/quarter_earnings.csv
```

What this command does:

- reads every CSV export in the `exports/` folder
- groups rows by participant label
- sums the detected payoff column
- writes one summary CSV to `dist/quarter_earnings.csv`

If your CSV uses unusual column names, the script also accepts overrides such as `--label-column` and `--payoff-column`.

## What Not To Store In The Repo

- student names or institutional IDs
- the private mapping from real names to pseudonymous labels
- raw gradebook files
- screenshots or exports containing personally identifying information
