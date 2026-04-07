#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DIST_DIR="$ROOT_DIR/dist"
PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
VERSION_FILE="$ROOT_DIR/VERSION"
if [[ ! -f "$VERSION_FILE" ]]; then
  echo "Missing VERSION file at $VERSION_FILE"
  exit 1
fi

if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="$(command -v python3)"
fi

PACKAGE_VERSION="$(tr -d '[:space:]' < "$VERSION_FILE")"
if [[ -z "$PACKAGE_VERSION" ]]; then
  echo "VERSION file is empty."
  exit 1
fi

PACKAGE_BASENAME="oTree_classroom_experiments_instructor_v${PACKAGE_VERSION}"
mkdir -p "$DIST_DIR"
zsh "$ROOT_DIR/scripts/build_instructor_pdfs.sh"
zsh "$ROOT_DIR/scripts/build_instructor_site.sh"
STAGING_ROOT="$(mktemp -d "$DIST_DIR/staging.XXXXXX")"
PACKAGE_ROOT="$STAGING_ROOT/oTree_classroom_experiments"
ZIP_PATH="$DIST_DIR/${PACKAGE_BASENAME}.zip"
CHECKSUM_PATH="$DIST_DIR/SHA256SUMS.txt"

mkdir -p "$PACKAGE_ROOT" "$PACKAGE_ROOT/docs" "$PACKAGE_ROOT/scripts" "$PACKAGE_ROOT/01_instructor_pdfs" "$PACKAGE_ROOT/02_docs_site"

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
  "$ROOT_DIR/VERSION" \
  "$ROOT_DIR/RELEASE_NOTES.md" \
  "$ROOT_DIR/.python-version" \
  "$ROOT_DIR/Procfile" \
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

while IFS=$'\t' read -r _ relative_path _ _; do
  copy_path "$ROOT_DIR/$relative_path" "$PACKAGE_ROOT/$relative_path"
done < <("$PYTHON_BIN" "$ROOT_DIR/scripts/instructor_docs.py" list)

for extra_doc in \
  "$ROOT_DIR/docs/instructor-onboarding-email.md"
do
  copy_path "$extra_doc" "$PACKAGE_ROOT/docs/"
done

copy_path "$ROOT_DIR/dist/01_instructor_pdfs" "$PACKAGE_ROOT/"
copy_path "$ROOT_DIR/dist/02_docs_site" "$PACKAGE_ROOT/"

for script_path in \
  "$ROOT_DIR/scripts/bootstrap.sh" \
  "$ROOT_DIR/scripts/build_instructor_pdfs.sh" \
  "$ROOT_DIR/scripts/build_instructor_pdfs.py" \
  "$ROOT_DIR/scripts/build_instructor_site.sh" \
  "$ROOT_DIR/scripts/build_instructor_site.py" \
  "$ROOT_DIR/scripts/build_quarter_earnings.py" \
  "$ROOT_DIR/scripts/audit_headcount_matrix.py" \
  "$ROOT_DIR/scripts/audit_instructor_docs.py" \
  "$ROOT_DIR/scripts/check_environment.py" \
  "$ROOT_DIR/scripts/generate_room_labels.py" \
  "$ROOT_DIR/scripts/instructor_docs.py" \
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

copy_path "$ROOT_DIR/tests" "$PACKAGE_ROOT/"

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

(
  cd "$DIST_DIR"
  shasum -a 256 "$(basename "$ZIP_PATH")" > "$CHECKSUM_PATH"
)

"$PYTHON_BIN" "$ROOT_DIR/scripts/verify_instructor_package.py" "$ZIP_PATH"

echo "Created instructor package: $ZIP_PATH"
echo "Wrote checksums: $CHECKSUM_PATH"
