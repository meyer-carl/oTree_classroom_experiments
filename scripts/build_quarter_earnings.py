from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path


LABEL_CANDIDATES = [
    "participant_label",
    "participant.label",
    "participant__label",
]
CODE_CANDIDATES = [
    "participant_code",
    "participant.code",
    "participant__code",
]
PAYOFF_CANDIDATES = [
    "payoff",
    "player.payoff",
    "participant.payoff",
    "payoff_plus_participation_fee",
]
SESSION_CANDIDATES = [
    "session_config_name",
    "session.config.name",
    "session_code",
    "session.code",
    "session__code",
]


def first_present(fieldnames: list[str], candidates: list[str]) -> str | None:
    for candidate in candidates:
        if candidate in fieldnames:
            return candidate
    return None


def format_decimal(value: Decimal) -> str:
    if value == value.to_integral():
        return str(int(value))
    return format(value.normalize(), "f")


def resolve_input_paths(raw_inputs: list[str]) -> list[Path]:
    resolved: list[Path] = []
    for raw_input in raw_inputs:
        input_path = Path(raw_input)
        if input_path.is_dir():
            resolved.extend(sorted(input_path.glob("*.csv")))
        else:
            resolved.append(input_path)
    unique_paths: list[Path] = []
    seen = set()
    for path in resolved:
        normalized = path.resolve()
        if normalized in seen:
            continue
        seen.add(normalized)
        unique_paths.append(normalized)
    return unique_paths


def parse_payoff(value: str, path: Path, row_number: int, column_name: str) -> Decimal:
    text = (value or "").strip()
    if not text:
        return Decimal("0")
    try:
        return Decimal(text)
    except InvalidOperation as exc:
        raise ValueError(
            f"Could not parse payoff value '{text}' in {path} row {row_number} column {column_name}."
        ) from exc


def aggregate_earnings(
    input_paths: list[Path],
    *,
    label_column: str | None = None,
    payoff_column: str | None = None,
    session_column: str | None = None,
    allow_anonymous: bool = False,
) -> dict[str, dict[str, object]]:
    if not input_paths:
        raise ValueError("No CSV inputs were provided.")

    aggregated: dict[str, dict[str, object]] = {}

    for input_path in input_paths:
        if not input_path.exists():
            raise FileNotFoundError(f"CSV input not found: {input_path}")

        with input_path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            fieldnames = reader.fieldnames or []
            active_label_column = label_column or first_present(fieldnames, LABEL_CANDIDATES)
            active_code_column = first_present(fieldnames, CODE_CANDIDATES)
            active_payoff_column = payoff_column or first_present(fieldnames, PAYOFF_CANDIDATES)
            active_session_column = session_column or first_present(fieldnames, SESSION_CANDIDATES)

            if not active_payoff_column:
                raise ValueError(
                    f"Could not find a payoff column in {input_path}. Pass --payoff-column explicitly."
                )

            for row_number, row in enumerate(reader, start=2):
                label = (row.get(active_label_column or "", "") or "").strip()
                if not label:
                    if allow_anonymous and active_code_column:
                        code = (row.get(active_code_column, "") or "").strip()
                        label = f"ANON_{code}" if code else ""
                    if not label:
                        raise ValueError(
                            f"Missing participant label in {input_path} row {row_number}. "
                            "Use tracked labels or pass --allow-anonymous with participant codes present."
                        )

                session_name = (
                    (row.get(active_session_column or "", "") or "").strip()
                    if active_session_column
                    else ""
                )
                payoff = parse_payoff(
                    row.get(active_payoff_column, ""),
                    input_path,
                    row_number,
                    active_payoff_column,
                )

                if label not in aggregated:
                    aggregated[label] = dict(
                        total_points=Decimal("0"),
                        row_count=0,
                        sessions=set(),
                        source_files=set(),
                    )

                entry = aggregated[label]
                entry["total_points"] = entry["total_points"] + payoff
                entry["row_count"] = entry["row_count"] + 1
                if session_name:
                    entry["sessions"].add(session_name)
                entry["source_files"].add(input_path.name)

    return aggregated


def write_summary(output_path: Path, aggregated: dict[str, dict[str, object]]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "participant_label",
                "total_points",
                "session_count",
                "row_count",
                "sessions",
                "source_files",
            ]
        )
        for participant_label in sorted(aggregated):
            entry = aggregated[participant_label]
            sessions = sorted(entry["sessions"])
            source_files = sorted(entry["source_files"])
            writer.writerow(
                [
                    participant_label,
                    format_decimal(entry["total_points"]),
                    len(sessions),
                    entry["row_count"],
                    ";".join(sessions),
                    ";".join(source_files),
                ]
            )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Aggregate quarter-long oTree earnings by participant label."
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        help="CSV files or directories containing CSV exports.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("dist/quarter_earnings.csv"),
        help="Output CSV path. Defaults to dist/quarter_earnings.csv.",
    )
    parser.add_argument(
        "--label-column",
        help="Override automatic participant-label column detection.",
    )
    parser.add_argument(
        "--payoff-column",
        help="Override automatic payoff-column detection.",
    )
    parser.add_argument(
        "--session-column",
        help="Override automatic session-name column detection.",
    )
    parser.add_argument(
        "--allow-anonymous",
        action="store_true",
        help="Permit missing participant labels when participant codes are present.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    input_paths = resolve_input_paths(args.inputs)
    aggregated = aggregate_earnings(
        input_paths,
        label_column=args.label_column,
        payoff_column=args.payoff_column,
        session_column=args.session_column,
        allow_anonymous=args.allow_anonymous,
    )
    write_summary(args.output, aggregated)
    print(f"Wrote quarter earnings summary to {args.output}")


if __name__ == "__main__":
    main()
