# Environment

## Local Runtime Assumptions

- The project expects a working Python environment with `otree` available.
- `requirements.txt` is the authoritative dependency anchor for the runtime.
- `db.sqlite3` is local state and can be recreated.

## Known Local Trap

There is a separate `otree/` directory under `/Users/carl/Documents/Teaching/` that can shadow the Python package name during local inspection. When that happens, imports may resolve to the docs site source tree instead of the oTree package.

## Practical Rule

- Before debugging app code, confirm which `otree` module the interpreter is resolving.
- If imports look wrong, fix the environment first rather than editing the apps.
