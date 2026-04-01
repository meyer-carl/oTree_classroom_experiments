from __future__ import annotations

import argparse
from pathlib import Path


def generate_labels(prefix: str, count: int, start: int = 1, digits: int = 3) -> list[str]:
    if count <= 0:
        raise ValueError("count must be positive")
    if start <= 0:
        raise ValueError("start must be positive")
    if digits <= 0:
        raise ValueError("digits must be positive")
    return [f"{prefix}_{index:0{digits}d}" for index in range(start, start + count)]


def write_labels(output_path: Path, labels: list[str], force: bool = False) -> None:
    if output_path.exists() and not force:
        raise FileExistsError(
            f"{output_path} already exists. Pass --force to overwrite it."
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(labels) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate pseudonymous oTree room labels such as ECON101_001."
    )
    parser.add_argument("--prefix", required=True, help="Label prefix, e.g. ECON101")
    parser.add_argument("--count", required=True, type=int, help="Number of labels to generate")
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Output text file, e.g. _rooms/econ101.txt",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=1,
        help="Starting numeric suffix. Defaults to 1.",
    )
    parser.add_argument(
        "--digits",
        type=int,
        default=3,
        help="Zero-padding width for the numeric suffix. Defaults to 3.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite the output file if it already exists.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    labels = generate_labels(
        prefix=args.prefix,
        count=args.count,
        start=args.start,
        digits=args.digits,
    )
    write_labels(args.output, labels, force=args.force)
    print(f"Wrote {len(labels)} labels to {args.output}")


if __name__ == "__main__":
    main()
