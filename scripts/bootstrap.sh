#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3.12}"
VENV_DIR="${VENV_DIR:-.venv}"

cat <<'EOF'
Bootstrapping oTree classroom experiments.

This script expects to run from the project root and avoids the unrelated
/Users/carl/Documents/Teaching/otree directory shadowing the real oTree package.
EOF

"$PYTHON_BIN" -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements-dev.txt

cat <<EOF

Bootstrap complete.
Activate the environment with:
  source "$VENV_DIR/bin/activate"

Then verify the install with:
  ./scripts/verify.sh
EOF
