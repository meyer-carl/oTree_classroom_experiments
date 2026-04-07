#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    from .instructor_docs import PDF_DIRNAME, ROOT, SITE_DIRNAME, load_manifest, ordered_pdf_paths
except ImportError:
    from instructor_docs import PDF_DIRNAME, ROOT, SITE_DIRNAME, load_manifest, ordered_pdf_paths


ROOT_DIR = ROOT
ABSOLUTE_PATH_RE = re.compile(r"/Users/[^)\s`]+")
TERMINAL_HINT_RE = re.compile(r"(Paste|Run).{0,50}Terminal", re.IGNORECASE)
RAW_MARKDOWN_REFERENCE_RE = re.compile(r"\b(?:\.\./)?(?:docs/)?[A-Za-z0-9_-]+\.md\b")
FORBIDDEN_PHRASES = (
    "## Planning Notes",
    "## When To Escalate",
)
FORBIDDEN_LEGACY_PATHS = (
    "02_instructor_website/",
    "02_instructor_site/",
)
PACKAGE_FOLDER = f"{PDF_DIRNAME}/"
SITE_FOLDER = f"{SITE_DIRNAME}/"


def iter_instructor_docs() -> list[Path]:
    manifest_docs = [entry.source_path for entry in load_manifest()]
    extras = [
        ROOT / "README.md",
        ROOT / "docs" / "hosting-and-deployment.md",
        ROOT / "docs" / "instructor-onboarding-email.md",
    ]
    unique: list[Path] = []
    seen = set()
    for path in manifest_docs + extras:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique.append(path)
    return unique


def check_manifest(errors: list[str]) -> None:
    entries = load_manifest()
    expected_orders = list(range(1, len(entries) + 1))
    actual_orders = [entry.order for entry in entries]
    if actual_orders != expected_orders:
        errors.append(f"Manifest order should be sequential starting at 1, found {actual_orders}.")
    for entry in entries:
        if not entry.source_path.exists():
            errors.append(f"Manifest source is missing: {entry.source_path}")


def check_doc_text(path: Path, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    if ABSOLUTE_PATH_RE.search(text):
        errors.append(f"{path.relative_to(ROOT)} contains an absolute local filesystem path.")
    for phrase in FORBIDDEN_PHRASES:
        if phrase in text:
            errors.append(f"{path.relative_to(ROOT)} contains internal-only section '{phrase}'.")
    for legacy_path in FORBIDDEN_LEGACY_PATHS:
        if legacy_path in text:
            errors.append(f"{path.relative_to(ROOT)} still refers to legacy package path '{legacy_path}'.")
    if path.name.endswith(".md"):
        for line in text.splitlines():
            if line.lstrip().startswith("|"):
                errors.append(f"{path.relative_to(ROOT)} still contains a Markdown table. Use stacked sections instead.")
                break
    if path != ROOT / "README.md" and RAW_MARKDOWN_REFERENCE_RE.search(text):
        errors.append(
            f"{path.relative_to(ROOT)} still references raw Markdown filenames. Point instructors to PDFs or the website instead."
        )

    lines = text.splitlines()
    inside_bash_block = False
    for index, line in enumerate(lines):
        if line.strip() == "```bash":
            inside_bash_block = True
            window = "\n".join(lines[max(0, index - 3):index])
            if not TERMINAL_HINT_RE.search(window):
                errors.append(
                    f"{path.relative_to(ROOT)} has a bash block without a nearby plain-language Terminal explanation."
                )
            continue
        if inside_bash_block and line.strip() == "```":
            inside_bash_block = False
            continue
        if inside_bash_block and len(line) > 88:
            errors.append(f"{path.relative_to(ROOT)} has a line longer than 88 characters near line {index + 1}.")
            break


def check_ordered_references(text: str, label: str, errors: list[str]) -> None:
    expected_sequence = ordered_pdf_paths()
    positions: list[int] = []
    for filename in expected_sequence:
        if filename not in text:
            errors.append(f"{label} should point to {filename}.")
        positions.append(text.find(filename))
    if positions != sorted(positions):
        errors.append(f"{label} should list the numbered PDFs in the canonical reading order.")


def check_subsequence(text: str, label: str, expected_sequence: list[str], errors: list[str]) -> None:
    positions: list[int] = []
    for filename in expected_sequence:
        if filename not in text:
            errors.append(f"{label} should point to {filename}.")
        positions.append(text.find(filename))
    if positions != sorted(positions):
        errors.append(f"{label} should mention the packaged docs in canonical order.")


def check_key_expectations(errors: list[str]) -> None:
    install_text = (ROOT / "docs" / "install-from-scratch.md").read_text(encoding="utf-8")
    if "Do I need to install oTree separately? No." not in install_text:
        errors.append("docs/install-from-scratch.md should explicitly say that oTree does not need a separate install.")
    if "including oTree" not in install_text:
        errors.append("docs/install-from-scratch.md should state that bootstrap installs oTree into the local .venv.")

    quickstart_text = (ROOT / "INSTRUCTOR_QUICKSTART.md").read_text(encoding="utf-8")
    email_text = (ROOT / "docs" / "instructor-onboarding-email.md").read_text(encoding="utf-8")
    check_ordered_references(quickstart_text, "INSTRUCTOR_QUICKSTART.md", errors)
    check_ordered_references(email_text, "docs/instructor-onboarding-email.md", errors)

    readme_text = (ROOT / "README.md").read_text(encoding="utf-8")
    check_subsequence(readme_text, "README.md", ordered_pdf_paths()[:8], errors)
    if PACKAGE_FOLDER not in quickstart_text:
        errors.append(f"INSTRUCTOR_QUICKSTART.md should refer to {PACKAGE_FOLDER} for the packaged PDFs.")
    if SITE_FOLDER not in quickstart_text:
        errors.append(f"INSTRUCTOR_QUICKSTART.md should mention {SITE_FOLDER} for the packaged website docs.")
    if "GitHub Student Developer Pack" not in (ROOT / "docs" / "hosting-and-deployment.md").read_text(encoding="utf-8"):
        errors.append("docs/hosting-and-deployment.md should mention GitHub Student Developer Pack Heroku credits.")
    if "Procfile" not in (ROOT / "docs" / "hosting-and-deployment.md").read_text(encoding="utf-8"):
        errors.append("docs/hosting-and-deployment.md should explain what Procfile is.")
    if f"{SITE_DIRNAME}/index.html" not in readme_text:
        errors.append(f"README.md should mention {SITE_DIRNAME}/index.html for the packaged website docs.")


def main() -> int:
    errors: list[str] = []
    check_manifest(errors)
    for path in iter_instructor_docs():
        check_doc_text(path, errors)
    check_key_expectations(errors)

    if errors:
        for error in errors:
            print(error)
        return 1

    print(f"Verified instructor docs for {len(iter_instructor_docs())} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
