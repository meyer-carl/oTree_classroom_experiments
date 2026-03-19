# Test Matrix

| Category | Minimum Coverage |
| --- | --- |
| All apps | Syntax check and one happy-path bot run. |
| Branchy apps | One alternate path or outcome test. |
| Guarded inputs | One invalid-input or submission-failure test. |
| Multiplayer classroom apps | Incomplete-group behavior and wait-page coordination. |
| Randomized flows | Deterministic assertions around the random choice, not the random seed itself. |
| Repeated-round apps | Group persistence, round history, and cumulative payoff checks. |

## Priority Order

1. `ab_ultimatum`
2. `ac_trust`
3. `af_centipede`
4. `ak_market_supply_demand`
5. `ai_prisoner_mult_rd`
