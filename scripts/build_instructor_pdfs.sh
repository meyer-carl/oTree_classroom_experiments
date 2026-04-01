#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
MANIFEST="$ROOT_DIR/docs/instructor-pdf-manifest.tsv"
OUT_DIR="$ROOT_DIR/dist/instructor_pdfs"

if [[ ! -f "$MANIFEST" ]]; then
  echo "Missing PDF manifest at $MANIFEST."
  exit 1
fi

for tool in pandoc xelatex; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "Missing required tool: $tool"
    exit 1
  fi
done

mkdir -p "$OUT_DIR"
existing_pdfs=("$OUT_DIR"/*.pdf(N))
if (( ${#existing_pdfs[@]} > 0 )); then
  rm -f "${existing_pdfs[@]}"
fi

common_args=(
  --from gfm
  --standalone
  --pdf-engine=xelatex
  -V geometry:margin=1in
)

combined_inputs=()

while IFS=$'\t' read -r relative_path slug title standalone; do
  [[ -z "$relative_path" ]] && continue
  [[ "$relative_path" == \#* ]] && continue

  source_path="$ROOT_DIR/$relative_path"
  if [[ ! -f "$source_path" ]]; then
    echo "Manifest entry points to a missing file: $relative_path"
    exit 1
  fi

  combined_inputs+=("$source_path")

  case "$standalone" in
    yes)
      pandoc "${common_args[@]}" \
        "$source_path" \
        --metadata "title=$title" \
        -o "$OUT_DIR/${slug}.pdf"
      ;;
    no)
      ;;
    *)
      echo "Invalid standalone flag '$standalone' for $relative_path"
      exit 1
      ;;
  esac
done < "$MANIFEST"

if [[ ${#combined_inputs[@]} -eq 0 ]]; then
  echo "The PDF manifest does not list any input files."
  exit 1
fi

pandoc "${common_args[@]}" \
  --toc \
  --toc-depth=2 \
  "${combined_inputs[@]}" \
  --metadata "title=Instructor Packet" \
  -o "$OUT_DIR/instructor_packet.pdf"

echo "Built instructor PDFs in $OUT_DIR"
