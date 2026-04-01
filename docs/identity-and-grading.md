# Identity and Grading

## Recommended Modes

Use one of these two modes on purpose. Do not mix them casually mid-quarter.

| Mode | Recommended Use | What Students See | Gradebook Compatibility |
| --- | --- | --- | --- |
| `tracked_pseudonymous` | Real classes where earnings may count toward participation or grades. | Stable pseudonymous labels such as `ECON101_001`. | Yes. Recommended default. |
| `fully_anonymous` | One-off demos, guest lectures, or sessions where no longitudinal tracking is needed. | Anonymous room entry or random aliases. | No, unless the instructor keeps a separate offline alias map. |

## Tracked Pseudonymous Workflow

1. Generate a room-label file with stable pseudonymous IDs:

```bash
python scripts/generate_room_labels.py \
  --prefix ECON101 \
  --count 40 \
  --output _rooms/econ101.txt \
  --force
```

2. Share those labels or their secure room URLs with students.
3. Keep the mapping from student name to pseudonymous label outside this repo.
4. Use the same labels for the full quarter so exports can be merged cleanly.

### Why This Is The Default

- It lets you track participation or earnings across sessions.
- It keeps classroom interaction pseudonymous instead of using student names.
- `payment_info` already shows `participant.label` when it exists, so students can confirm their own code at the end of a run.

## Fully Anonymous Workflow

- Use the unlabeled `live_demo` room or another room with no `participant_label_file`.
- Do not promise quarter-long grade linkage from these sessions.
- If you later decide you need grading, create a separate offline alias map before the session begins. Do not try to reconstruct identities from anonymous exports after the fact.

## Secure Room URLs

- Labeled rooms should use secure URLs.
- Secure URLs stop students from changing `participant_label` manually to impersonate another student.
- If you are running a tracked class, do not disable this protection for convenience.

## Payment Screen Behavior

`payment_info` displays:

- the participant label when the session uses labeled rooms or labeled start URLs
- the anonymous oTree participant code when no label is present

That means:

- pseudonymous tracked sessions are naturally compatible with a private gradebook
- fully anonymous sessions remain anonymous in the app itself

## Quarter Earnings Workflow

After each class:

1. Export the session data.
2. Save the export with a course-date-app filename.
3. Keep the session config name and room name with the export.

When you want a quarter summary:

```bash
python scripts/build_quarter_earnings.py exports/ --output dist/quarter_earnings.csv
```

The script:

- groups rows by participant label
- sums the detected payoff column
- lists which sessions and source files contributed to each total

If your CSV uses nonstandard column names, pass explicit overrides such as `--label-column` or `--payoff-column`.

## What Not To Store In The Repo

- Student names or institutional IDs
- The private mapping from real names to pseudonymous labels
- Raw gradebook files
- Screenshots or exports containing personally identifying information

## Practical Defaults

- Use pseudonymous labels like `ECON101_001`, not names like `Alice` or `Bob`.
- Keep one room per course or section.
- Reuse the same labels all quarter.
- Treat anonymous mode as incompatible with grade-linked earnings unless you maintain a separate offline key yourself.
