#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOP_LEVEL = "oTree_classroom_experiments/"
REQUIRED_PATHS = {
    f"{TOP_LEVEL}README.md",
    f"{TOP_LEVEL}INSTRUCTOR_QUICKSTART.md",
    f"{TOP_LEVEL}VERSION",
    f"{TOP_LEVEL}RELEASE_NOTES.md",
    f"{TOP_LEVEL}01_instructor_pdfs/",
    f"{TOP_LEVEL}01_instructor_pdfs/00_instructor_packet.pdf",
    f"{TOP_LEVEL}01_instructor_pdfs/01_install_from_scratch.pdf",
    f"{TOP_LEVEL}01_instructor_pdfs/02_instructor_quickstart.pdf",
    f"{TOP_LEVEL}01_instructor_pdfs/03_hosting_and_deployment.pdf",
    f"{TOP_LEVEL}01_instructor_pdfs/04_identity_and_grading.pdf",
    f"{TOP_LEVEL}01_instructor_pdfs/05_classroom_readiness.pdf",
    f"{TOP_LEVEL}01_instructor_pdfs/06_experiment_catalog.pdf",
    f"{TOP_LEVEL}01_instructor_pdfs/07_headcount_and_fallbacks.pdf",
    f"{TOP_LEVEL}01_instructor_pdfs/08_instructor_runbook.pdf",
    f"{TOP_LEVEL}01_instructor_pdfs/09_data_and_export.pdf",
    f"{TOP_LEVEL}01_instructor_pdfs/10_troubleshooting.pdf",
    f"{TOP_LEVEL}02_docs_site/",
    f"{TOP_LEVEL}02_docs_site/index.html",
}
FORBIDDEN_SUBSTRINGS = (
    "/.venv/",
    "/db.sqlite3",
    "/.codex/",
    "/principled_review_runs/",
    "/docs/project/",
    "/docs/contributor-guide.md",
    "/docs/instructor-docs-manifest.tsv",
    "/AGENTS.md",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify the packaged instructor ZIP boundary.")
    parser.add_argument("zip_path", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    zip_path = args.zip_path
    if not zip_path.exists():
        print(f"Missing ZIP artifact: {zip_path}")
        return 1

    with zipfile.ZipFile(zip_path) as archive:
        names = archive.namelist()

    errors: list[str] = []
    top_levels = {name.split("/", 1)[0] for name in names if name}
    if top_levels != {"oTree_classroom_experiments"}:
        errors.append(f"ZIP should unpack into a single top-level folder, found: {sorted(top_levels)}")

    name_set = set(names)
    for required in REQUIRED_PATHS:
        if required not in name_set:
            errors.append(f"Missing required packaged path: {required}")

    for name in names:
        for forbidden in FORBIDDEN_SUBSTRINGS:
            if forbidden in f"/{name}".replace("//", "/"):
                errors.append(f"Forbidden packaged path: {name}")
                break

    if errors:
        for error in errors:
            print(error)
        return 1

    print(f"Verified instructor package: {zip_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
