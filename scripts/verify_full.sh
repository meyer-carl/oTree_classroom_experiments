#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

PROJECT_PYTHON="$ROOT_DIR/.venv/bin/python"
if [[ ! -x "$PROJECT_PYTHON" ]]; then
  echo "Project virtualenv not found at $PROJECT_PYTHON. Run ./scripts/bootstrap.sh first."
  exit 1
fi

zsh ./scripts/run_preflight.sh
zsh ./scripts/build_instructor_pdfs.sh
"$PROJECT_PYTHON" scripts/run_session_suite.py full
