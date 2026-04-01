# Troubleshooting

## Common Problems

| Symptom | Likely Cause | Fix |
| --- | --- | --- |
| Participant is unmatched | Group is incomplete | Confirm room size or let the app skip to the next session item. |
| Session appears stuck | Wait page is waiting for another player | Check whether a browser was abandoned or a participant left the room. |
| Strategy-method page is confusing | The class was not warned ahead of time | Pause and restate the rule before continuing. |
| Payoff looks wrong | Bad headcount, wrong round, or invalid input | Check the bot test case and the app’s payoff invariant. |
| Export missing expected fields | The app did not write the field to player/group/session state | Update the model and export notes together. |
| Student used the wrong room or label | Wrong link or mistyped participant label | Move the student before launching, or verify the secure labeled URL and retry. |
| Student refreshed and seems duplicated | Duplicate tab or duplicate participation | Check the admin page before assigning a replacement seat. |
| Market app has one missing trader | Final group is incomplete | Do not launch. Use a reserve browser or switch apps. |

## Live Recovery Rules

- Do not restart the database unless the session is disposable.
- If an app depends on random paying rounds, record the chosen round before moving on.
- If a browser is lost mid-class, decide whether to wait, replace, or skip the participant based on the app’s logic.
- For classroom demos, prefer a controlled skip over a long stall.
- If a student arrives after a multiplayer session has begun, check `docs/headcount-and-fallbacks.md` before seating them.
- If a timed app confused the room, stop and restate the rule instead of silently letting the timeout decide the lesson.

## When To Escalate

- If unmatched handling differs between apps, document it immediately in the relevant playbook.
- If a timeout path is untested, add a bot case before the next live class.
- If a repeated-round app carries state forward unexpectedly, treat it as a release-blocking issue.
