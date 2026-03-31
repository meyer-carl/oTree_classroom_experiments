#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DIST_DIR="$ROOT_DIR/dist"
PACKAGE_BASENAME="oTree_classroom_experiments_instructor_$(date +%Y%m%d)"
mkdir -p "$DIST_DIR"
STAGING_ROOT="$(mktemp -d "$DIST_DIR/staging.XXXXXX")"
PACKAGE_ROOT="$STAGING_ROOT/oTree_classroom_experiments"
ZIP_PATH="$DIST_DIR/${PACKAGE_BASENAME}.zip"

mkdir -p "$PACKAGE_ROOT" "$PACKAGE_ROOT/docs" "$PACKAGE_ROOT/scripts"

copy_path() {
  local source_path="$1"
  local destination_path="$2"
  mkdir -p "$(dirname "$destination_path")"
  rsync -a \
    --exclude '__pycache__/' \
    --exclude '.pytest_cache/' \
    --exclude '.ruff_cache/' \
    --exclude '.DS_Store' \
    --exclude '*.py[cod]' \
    "$source_path" "$destination_path"
}

cleanup() {
  rm -rf "$STAGING_ROOT"
}
trap cleanup EXIT

for file_path in \
  "$ROOT_DIR/README.md" \
  "$ROOT_DIR/INSTRUCTOR_QUICKSTART.md" \
  "$ROOT_DIR/LICENSE" \
  "$ROOT_DIR/.python-version" \
  "$ROOT_DIR/requirements.txt" \
  "$ROOT_DIR/requirements-dev.txt" \
  "$ROOT_DIR/settings.py" \
  "$ROOT_DIR/classroom_utils.py"
do
  copy_path "$file_path" "$PACKAGE_ROOT/"
done

for dir_path in \
  "$ROOT_DIR/_rooms" \
  "$ROOT_DIR/_static" \
  "$ROOT_DIR/_templates"
do
  copy_path "$dir_path" "$PACKAGE_ROOT/"
done

for doc_path in "$ROOT_DIR"/docs/*.md; do
  copy_path "$doc_path" "$PACKAGE_ROOT/docs/"
done

for script_path in \
  "$ROOT_DIR/scripts/bootstrap.sh" \
  "$ROOT_DIR/scripts/check_environment.py" \
  "$ROOT_DIR/scripts/run_preflight.sh" \
  "$ROOT_DIR/scripts/run_session_suite.py" \
  "$ROOT_DIR/scripts/session_suites.py" \
  "$ROOT_DIR/scripts/verify.sh" \
  "$ROOT_DIR/scripts/verify_audit_tests.py" \
  "$ROOT_DIR/scripts/verify_full.sh" \
  "$ROOT_DIR/scripts/verify_high_coverage.sh" \
  "$ROOT_DIR/scripts/verify_test_coverage.py"
do
  copy_path "$script_path" "$PACKAGE_ROOT/scripts/"
done

for app_dir in "$ROOT_DIR"/*; do
  if [[ -d "$app_dir" && -f "$app_dir/__init__.py" ]]; then
    copy_path "$app_dir" "$PACKAGE_ROOT/"
  fi
done

rm -f "$ZIP_PATH"
(
  cd "$STAGING_ROOT"
  zip -qr "$ZIP_PATH" "oTree_classroom_experiments"
)

echo "Created instructor package: $ZIP_PATH"
