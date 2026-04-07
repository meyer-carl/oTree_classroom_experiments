#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from instructor_docs import GENERATED_SITE_DOCS_DIR, ROOT, SITE_OUTPUT_DIR, build_site_source, load_manifest


STYLE_CSS = """
body {
  font-family: Georgia, serif;
  line-height: 1.6;
  margin: 0 auto;
  max-width: 900px;
  padding: 2rem 1.5rem 4rem;
  color: #1f2933;
  background: #f9fafb;
}
h1, h2, h3 {
  color: #102a43;
}
a {
  color: #0b5fff;
}
code {
  background: #eaf2ff;
  padding: 0.1rem 0.3rem;
}
pre code {
  display: block;
  overflow-x: auto;
  padding: 1rem;
  background: #102a43;
  color: #f0f4f8;
}
blockquote {
  border-left: 4px solid #bcccdc;
  margin-left: 0;
  padding-left: 1rem;
}
"""


def require_tool(name: str) -> None:
    if shutil.which(name) is None:
        raise SystemExit(f"Missing required tool: {name}")


def build_html(source_dir: Path, output_dir: Path) -> None:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "style.css").write_text(STYLE_CSS.strip() + "\n", encoding="utf-8")

    manifest = load_manifest()
    title_map = {entry.site_markdown_name: entry.title for entry in manifest}
    title_map["index.md"] = "Instructor Documentation"

    for markdown_path in sorted(source_dir.glob("*.md")):
        output_name = markdown_path.with_suffix(".html").name
        title = title_map[markdown_path.name]
        subprocess.run(
            [
                "pandoc",
                "--from",
                "gfm",
                "--standalone",
                "--metadata",
                f"title={title}",
                "--css",
                "style.css",
                str(markdown_path),
                "-o",
                str(output_dir / output_name),
            ],
            cwd=ROOT,
            check=True,
        )


def main() -> None:
    require_tool("pandoc")
    docs = load_manifest()
    build_site_source(GENERATED_SITE_DOCS_DIR, docs)
    build_html(GENERATED_SITE_DOCS_DIR, SITE_OUTPUT_DIR)
    print(f"Built instructor website in {SITE_OUTPUT_DIR}")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        sys.exit(exc.returncode)
