# Test Matrix

## Suites

| Suite | Purpose | Coverage |
| --- | --- | --- |
| `smoke` | Fast local gate for everyday changes. | Preflight checks plus 14 core session configs. |
| `high` | Main pre-share and pre-class automated gate. | All standalone and materially distinct session configs. |
| `full` | Release-level automated sweep. | All session configs, including survey/payment classroom bundles. |

## Minimum Coverage Rules

| Category | Minimum Coverage |
| --- | --- |
| All apps | Syntax check and one happy-path bot run. |
| Branchy apps | One alternate path or outcome test. |
| Guarded inputs | One invalid-input or submission-failure test. |
| Multiplayer classroom apps | Incomplete-group behavior and wait-page coordination. |
| Randomized flows | Deterministic assertions around the random choice, not the random seed itself. |
| Repeated-round apps | Group persistence, round history, cumulative payoff checks, and paying-round branches when configured. |

## Priority Order

1. `ab_ultimatum`
2. `ac_trust`
3. `af_centipede`
4. `ak_market_supply_demand`
5. `ai_prisoner_mult_rd`

## Commands

- `./scripts/bootstrap.sh`: create the project-local `.venv` used by the test runners.
- `./scripts/verify.sh`: run the smoke gate with the project-local `.venv`.
- `./scripts/verify_high_coverage.sh`: run the high-coverage gate before sharing the repo or using it in class.
- `./scripts/verify_full.sh`: run the exhaustive session sweep before releases or major deployments.

## Manual Release Gate

- Create one bundled classroom session with survey and payment flow.
- Run one strategy-method app with an odd headcount.
- Run one large-group market app.
- Confirm participant labels and room flow work as expected.
- Export results and confirm the output is interpretable without source-code inspection.
