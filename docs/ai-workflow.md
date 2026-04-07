# AI Workflow

## Recommended Loop

1. Plan the change.
2. Implement in the smallest safe batch.
3. Hand the result to a fresh-context reviewer agent.
4. Revise based on the reviewer’s findings.
5. Verify with tests or documentation checks.

## Suggested Agent Roles

- Audit agent: map the repo and identify risk.
- Test agent: add bot coverage and invariant checks.
- Instructor-ops agent: keep live-class docs accurate.
- Syllabus agent: find missing topics and rank additions.
- Docs agent: package the final shareable material.

## Context Pack

Always consult the files in `docs/project/` before starting a new task. That pack is the stable memory for the project and should be updated whenever a decision changes.

## Skill Use

Use the Codex skills in `.codex/skills/` when the task matches their scope. The skills are intentionally narrow so future agents can follow the same process without re-deriving it.

Treat `.codex/skills/` and `.codex/scripts/` as read-only control-plane content. Put runtime artifacts in `.codex/cache/`, `.codex/out/`, `.codex/runs/`, `.codex/logs/`, or `.codex/worktrees/` instead of inventing new repo-root run folders.

If you need historical principled-review artifacts, read `.codex/runs/principled-review/` first and fall back to `principled_review_runs/`.

## Review Standard

Do not trust a single implementation pass on classroom-critical code. Use one agent to write and a separate agent to challenge the assumptions.
