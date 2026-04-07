from __future__ import annotations

import shutil
import subprocess
import sys

from instructor_docs import PDF_OUTPUT_DIR, ROOT, load_manifest


def require_tool(name: str) -> None:
    if shutil.which(name) is None:
        raise SystemExit(f"Missing required tool: {name}")


def main() -> None:
    for tool in ("pandoc", "xelatex"):
        require_tool(tool)

    PDF_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for pdf in PDF_OUTPUT_DIR.glob("*.pdf"):
        pdf.unlink()

    common_args = [
        "pandoc",
        "--from",
        "gfm",
        "--standalone",
        "--pdf-engine=xelatex",
        "-V",
        "geometry:margin=1in",
    ]

    combined_inputs: list[str] = []
    docs = load_manifest()
    for doc in docs:
        combined_inputs.append(str(doc.source_abspath))
        if doc.standalone:
            subprocess.run(
                common_args
                + [
                    str(doc.source_abspath),
                    "--metadata",
                    f"title={doc.title}",
                    "-o",
                    str(PDF_OUTPUT_DIR / doc.package_pdf_name),
                ],
                cwd=ROOT,
                check=True,
            )

    subprocess.run(
        common_args
        + [
            "--toc",
            "--toc-depth=2",
            *combined_inputs,
            "--metadata",
            "title=Instructor Packet",
            "-o",
            str(PDF_OUTPUT_DIR / "00_instructor_packet.pdf"),
        ],
        cwd=ROOT,
        check=True,
    )
    print(f"Built instructor PDFs in {PDF_OUTPUT_DIR}")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        sys.exit(exc.returncode)
