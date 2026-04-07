#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

PROJECT_PYTHON="$ROOT_DIR/.venv/bin/python"
if [[ ! -x "$PROJECT_PYTHON" ]]; then
  PROJECT_PYTHON="$(command -v python3)"
fi

"$PROJECT_PYTHON" "$ROOT_DIR/scripts/build_instructor_site.py"
