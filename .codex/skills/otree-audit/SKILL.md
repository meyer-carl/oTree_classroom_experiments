---
name: otree-audit
description: Audit oTree classroom repos for experiment inventory, risk concentration, workflow gaps, and documentation needs.
---

# oTree Audit

Use this skill when mapping an oTree classroom repository before code changes.

## Workflow

1. Read `docs/project/inventory.md`.
2. Read `docs/project/risk-matrix.md` and `docs/project/test-matrix.md`.
3. Identify the top-risk apps and shared support paths.
4. Summarize what is missing from instructor-facing docs.
5. Write findings into `docs/project/decision-log.md` if the audit changes a durable assumption.

## Output

- Inventory of experiment categories.
- Top risk modules.
- Missing operational docs.
- Recommended first review order.

## Keep In Mind

- Prioritize live-class failure modes.
- Separate app logic risk from documentation risk.
- Prefer a small set of high-value recommendations.
