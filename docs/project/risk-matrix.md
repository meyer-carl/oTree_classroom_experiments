# Risk Matrix

| Area | Risk | Why It Matters | Mitigation |
| --- | --- | --- | --- |
| `af_centipede` | High | Dense state machine and strategy fallback logic | Deep deterministic tests and explicit instructor docs. |
| `ac_trust` | High | Random second-mover substitution in incomplete groups | Document fallback rules and test both modes. |
| `ab_ultimatum` | High | Strategy-method branch changes the game flow | Add explicit branch tests and instructor notes. |
| `ak_market_supply_demand` | High | Large headcount and role assignment | Validate role/value assignment and no-trade cases. |
| `as_competitiveness` | Medium | Timed task plus incentive selection | Test timeout and payoff selection behavior. |
| `ai_prisoner_mult_rd` | Medium | Repeated-round state and random paying round | Test round linking and payoff accumulation. |
| `survey` / `payment_info` | Medium | Operationally useful but easy to forget | Fold into standard session docs. |
