# Inventory

## Current Shape

- 27 apps are present, plus `survey` and `payment_info` as support apps.
- The catalog is strongest in social preferences, auctions, and strategic games.
- Shared infrastructure is intentionally light: a room file, a shared unmatched template, and a single session config file.

## Operational Facts

- `settings.py` is the authoritative source for session names and room setup.
- `game_overview.tex` is the current parameter catalog, but it is not enough for operational reuse by itself.
- The repository needs docs that explain how to run, test, and share the experiments, not just what they do.

## Risk Concentration

- Strategy-method apps.
- Large-group markets.
- Repeated-round games with random paying rounds.
- Timed tasks and any app with incomplete-group behavior.
