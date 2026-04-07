# Agent Operating Notes

This repository is organized for collaborative agent work. The rules below keep changes reviewable and prevent agents from rediscovering the same project facts.

## Before Editing

1. Read `docs/project/inventory.md`.
2. Read `docs/project/risk-matrix.md` and `docs/project/test-matrix.md`.
3. Check `docs/project/decision-log.md` for current assumptions.
4. Prefer the smallest file set that satisfies the task.

## Work Style

- Keep edits within the assigned scope.
- Do not revert unrelated user changes.
- Use `apply_patch` for file edits.
- Prefer small, verifiable batches over broad rewrites.
- Add or update docs when behavior changes.
- Write generated runtime state only under `.codex/cache/`, `.codex/out/`, `.codex/runs/`, `.codex/logs/`, or `.codex/worktrees/`.
- Treat legacy `principled_review_runs/` as a compatibility read surface, not a default write target.

## Codex Layout

- Keep control-plane assets read-only under `.codex/skills/` and `.codex/scripts/`.
- Treat `.codex/cache/`, `.codex/out/`, `.codex/runs/`, `.codex/logs/`, and `.codex/worktrees/` as the repo-local writable surfaces.
- Keep durable instructor-facing outputs in `dist/` and the explicitly named docs files, not inside broad writable docs trees.

## Verification

- For docs work, confirm links, file names, and navigation are accurate.
- For test or code work, add the minimal test coverage needed to protect the new behavior.
- If a change affects classroom operations, update the runbook or troubleshooting notes in the same branch.

## Agent Roles

- `otree-audit`: inventory, risk, and gap analysis.
- `otree-test-author`: bot tests and invariant checks.
- `classroom-runbook`: instructor-facing workflow and live-session guidance.
- `syllabus-gap-scan`: source-grounded topic coverage and extension prioritization.

## Review Standard

Every nontrivial change should answer three questions:

- What changed?
- How do we know it works?
- What should an instructor do when it fails?
