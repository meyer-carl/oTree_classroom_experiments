#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
import shutil
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROOT_DIR = ROOT
MANIFEST_PATH = ROOT / "docs" / "instructor-docs-manifest.tsv"
PDF_DIRNAME = "01_instructor_pdfs"
SITE_DIRNAME = "02_docs_site"
PDF_OUTPUT_DIR = ROOT / "dist" / PDF_DIRNAME
SITE_OUTPUT_DIR = ROOT / "dist" / SITE_DIRNAME
GENERATED_SITE_DOCS_DIR = ROOT / ".generated" / "instructor_site_docs"
LINK_PATTERN = re.compile(r"(\[[^\]]+\]\()([^)]+)(\))")


@dataclass(frozen=True)
class DocEntry:
    order: int
    source_path: Path
    site_path: str
    slug: str
    title: str
    standalone: bool
    audience: str

    @property
    def package_pdf_name(self) -> str:
        return f"{self.order:02d}_{self.slug}.pdf"

    @property
    def package_label(self) -> str:
        return f"{self.order:02d} {self.title}"

    @property
    def source_abspath(self) -> Path:
        return self.source_path

    @property
    def site_markdown_name(self) -> str:
        return self.site_path

    @property
    def site_html_name(self) -> str:
        return str(Path(self.site_path).with_suffix(".html"))


def load_manifest(manifest_path: Path = MANIFEST_PATH) -> list[DocEntry]:
    entries: list[DocEntry] = []
    with manifest_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        for row in reader:
            if not row or row[0].startswith("#"):
                continue
            if len(row) != 7:
                raise ValueError(f"Invalid manifest row: {row}")
            order_text, relative_path, site_path, slug, title, standalone, audience = row
            source_path = ROOT / relative_path
            entries.append(
                DocEntry(
                    order=int(order_text),
                    source_path=source_path,
                    site_path=site_path,
                    slug=slug,
                    title=title,
                    standalone=standalone == "yes",
                    audience=audience,
                )
            )
    return sorted(entries, key=lambda entry: entry.order)


def ordered_pdf_names(entries: list[DocEntry] | None = None) -> list[str]:
    manifest_entries = entries or load_manifest()
    return [entry.package_pdf_name for entry in manifest_entries if entry.standalone]


def ordered_pdf_paths(folder_name: str = PDF_DIRNAME) -> list[str]:
    return [f"{folder_name}/{name}" for name in ordered_pdf_names()]


def _site_target_map(entries: list[DocEntry]) -> dict[Path, str]:
    return {entry.source_path.resolve(): entry.site_html_name for entry in entries}


def rewrite_internal_links(text: str, source_path: Path, entries: list[DocEntry]) -> str:
    site_targets = _site_target_map(entries)

    def replace(match: re.Match[str]) -> str:
        prefix, target, suffix = match.groups()
        if "://" in target or target.startswith("#") or target.startswith("mailto:"):
            return match.group(0)

        path_part, hash_mark, anchor = target.partition("#")
        if not path_part:
            return match.group(0)

        resolved = (source_path.parent / path_part).resolve()
        if resolved == (ROOT / "README.md").resolve():
            new_target = "index.html"
        else:
            new_target = site_targets.get(resolved)
        if not new_target:
            return match.group(0)
        if hash_mark:
            new_target = f"{new_target}#{anchor}"
        return f"{prefix}{new_target}{suffix}"

    return LINK_PATTERN.sub(replace, text)


def _nav_block(entries: list[DocEntry], index: int) -> str:
    previous_target = "index.html" if index == 0 else entries[index - 1].site_html_name
    previous_label = "Start Here" if index == 0 else f"{entries[index - 1].order:02d} {entries[index - 1].title}"
    next_exists = index + 1 < len(entries)
    next_target = entries[index + 1].site_html_name if next_exists else "index.html"
    next_label = f"{entries[index + 1].order:02d} {entries[index + 1].title}" if next_exists else "Start Here"
    return "\n".join(
        [
            f"[Home](index.html) | [Previous: {previous_label}]({previous_target}) | [Next: {next_label}]({next_target})",
            "",
        ]
    )


def render_index(entries: list[DocEntry]) -> str:
    lines = [
        "# Instructor Documentation",
        "",
        f"This site mirrors the instructor packet and keeps the same reading order as the numbered PDFs in `{PDF_DIRNAME}/`.",
        "",
        "## Read In This Order",
        "",
    ]
    for entry in entries:
        lines.append(f"{entry.order}. [{entry.title}]({entry.site_html_name})")
    lines.extend(
        [
            "",
            "## Package Formats",
            "",
            f"- Open `{PDF_DIRNAME}/00_instructor_packet.pdf` if you prefer a single PDF.",
            "- Open the numbered PDFs if you want one short document at a time.",
            "- Use this site if you want clickable navigation between the same documents.",
        ]
    )
    return "\n".join(lines) + "\n"


def build_site_source(output_dir: Path, entries: list[DocEntry]) -> None:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / "index.md").write_text(render_index(entries), encoding="utf-8")
    for index, entry in enumerate(entries):
        destination = output_dir / entry.site_markdown_name
        destination.parent.mkdir(parents=True, exist_ok=True)
        source_text = entry.source_path.read_text(encoding="utf-8")
        rendered = rewrite_internal_links(source_text, entry.source_path, entries)
        destination.write_text(
            _nav_block(entries, index) + rendered + "\n\n" + _nav_block(entries, index),
            encoding="utf-8",
        )


def ensure_manifest_files_exist() -> None:
    missing = [str(entry.source_path.relative_to(ROOT)) for entry in load_manifest() if not entry.source_path.exists()]
    if missing:
        raise FileNotFoundError("Missing instructor doc sources:\n" + "\n".join(missing))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Utilities for instructor-facing docs.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    site_source = subparsers.add_parser("build-site-source", help="Build a temporary static-site source tree.")
    site_source.add_argument("--output", type=Path, required=True)

    subparsers.add_parser("list", help="Print manifest entries.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    entries = load_manifest()

    if args.command == "build-site-source":
        build_site_source(args.output, entries)
    elif args.command == "list":
        for entry in entries:
            print(
                f"{entry.order:02d}\t{entry.source_path.relative_to(ROOT)}\t{entry.package_pdf_name}\t{entry.title}"
            )


if __name__ == "__main__":
    main()
