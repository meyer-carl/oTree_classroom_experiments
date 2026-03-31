# oTree Classroom Experiments

Instructor-first oTree package for live behavioral and experimental economics classes.

This repository contains a catalog of classroom-ready experiments, shared templates, and the operational notes needed to run sessions reliably in person or online. The main design goal is repeatability: a new instructor should be able to install the project, launch a session, recover from a messy room, and export data without needing the original author present.

## Start Here

1. Send new instructors to [INSTRUCTOR_QUICKSTART.md](INSTRUCTOR_QUICKSTART.md) first.
2. Run `./scripts/bootstrap.sh` once to create the project-local `.venv`.
3. Run `./scripts/verify.sh` to confirm the repo-local environment works.
4. Read [docs/instructor-runbook.md](docs/instructor-runbook.md).
5. Scan [docs/experiment-catalog.md](docs/experiment-catalog.md) to choose the right app for a class topic.
6. Review [docs/classroom-playbooks.md](docs/classroom-playbooks.md) before a live session.
7. Use [docs/troubleshooting.md](docs/troubleshooting.md) when something stalls.
8. Follow [docs/data-and-export.md](docs/data-and-export.md) for exports and cleanup.

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
- Check `docs/project/environment.md` before debugging imports or runtime setup.

## Existing Support Apps

- `survey`: demographics and cognitive reflection items.
- `payment_info`: payout/redemption instructions.
- First-wave extensions now include `az_endowment_effect`, `ba_gift_exchange`, `bb_common_pool_resource`, `bc_asset_market_bubble`, and the loss-aversion and ambiguity-aversion modules in `ar_risk_time_preferences`.

These are intentionally documented here so instructors can fold them into standard class flows rather than leaving them as orphaned helpers.
