# oTree Classroom Experiments

Instructor-first oTree package for live behavioral and experimental economics classes.

This repository contains a catalog of classroom-ready experiments, shared templates, and the operational notes needed to run sessions reliably in person or online. The main design goal is repeatability: a new instructor should be able to install the project, launch a session, recover from a messy room, and export data without needing the original author present.

## Start Here

1. Send new instructors to [INSTRUCTOR_QUICKSTART.md](INSTRUCTOR_QUICKSTART.md) first.
2. If the computer is blank, read [docs/install-from-scratch.md](docs/install-from-scratch.md) before anything else.
3. Run `./scripts/bootstrap.sh` once to create the project-local `.venv`.
4. Run `./scripts/verify.sh` to confirm the repo-local environment works.
5. If you want printable instructor materials, run `./scripts/build_instructor_pdfs.sh`.
6. Read [docs/hosting-and-deployment.md](docs/hosting-and-deployment.md) before the first live class.
7. Read [docs/classroom-readiness.md](docs/classroom-readiness.md) and [docs/identity-and-grading.md](docs/identity-and-grading.md).
8. Read [docs/instructor-runbook.md](docs/instructor-runbook.md).
9. Scan [docs/experiment-catalog.md](docs/experiment-catalog.md) and [docs/headcount-and-fallbacks.md](docs/headcount-and-fallbacks.md) before choosing the class app.
10. Review [docs/classroom-playbooks.md](docs/classroom-playbooks.md) before a live session.
11. Use [docs/troubleshooting.md](docs/troubleshooting.md) when something stalls.
12. Follow [docs/data-and-export.md](docs/data-and-export.md) for exports and cleanup.

If you are a non-technical instructor, download the packaged ZIP from the latest GitHub Release rather than using the repository directly.

## Repository Map

- `settings.py`: session catalog and room setup.
- `_rooms/`: participant label files.
- `_templates/global/`: shared templates such as unmatched-player handling.
- `docs/project/`: internal context pack for future maintenance.
- `.codex/skills/`: Codex skills for repeatable audit and documentation work.

## Operating Principles

- Keep session names and URLs stable.
- Prefer deterministic bot coverage for classroom-critical paths.
- Document instructor workflow before adding more experiments.
- Treat `db.sqlite3` as disposable local state.
- Favor short, explicit docs that can be reused by others.
- Keep labeled rooms secure and keep real-name mappings outside the repo.

## Existing Support Apps

- `survey`: demographics and cognitive reflection items.
- `payment_info`: payout/redemption instructions.
- First-wave extensions now include `az_endowment_effect`, `ba_gift_exchange`, `bb_common_pool_resource`, `bc_asset_market_bubble`, and the loss-aversion and ambiguity-aversion modules in `ar_risk_time_preferences`.

These are intentionally documented here so instructors can fold them into standard class flows rather than leaving them as orphaned helpers.

## Release Info

- Current release version: see `VERSION`
- Release summary: see `RELEASE_NOTES.md`
- If you share the packaged ZIP, include `SHA256SUMS.txt` so recipients can verify the artifact they received
- Non-technical instructors should download the latest packaged ZIP from the GitHub Releases page

## Support

- This package is maintained by the instructor or repository owner distributing it.
- If you received a ZIP package directly, contact the person who sent it to you for support.
- When reporting a problem, include your operating system, the step that failed, the exact command or error message, and whether you were using local setup, `Heroku`, or `ngrok`.
- For local recovery steps, start with `docs/troubleshooting.md`.
