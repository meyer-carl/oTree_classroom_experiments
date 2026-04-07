from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from grading_benchmarks import (
    SessionContext,
    ZERO,
    collect_opportunities,
    missing_supported_apps,
    parse_decimal,
)


LABEL_CANDIDATES = [
    "participant.label",
    "participant_label",
    "participant__label",
]
CODE_CANDIDATES = [
    "participant.code",
    "participant_code",
    "participant__code",
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


def format_percentile(value: float | None) -> str:
    if value is None:
        return ""
    if value.is_integer():
        return str(int(value))
    return f"{value:.2f}"


def resolve_input_paths(raw_inputs: list[str]) -> list[Path]:
    resolved: list[Path] = []
    for raw_input in raw_inputs:
        input_path = Path(raw_input)
        if input_path.is_dir():
            direct_wide = sorted(input_path.glob("all_apps_wide.csv"))
            recursive_wide = sorted(path for path in input_path.rglob("all_apps_wide.csv") if path not in direct_wide)
            if direct_wide or recursive_wide:
                resolved.extend(direct_wide)
                resolved.extend(recursive_wide)
            else:
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


def load_wide_rows(input_paths: list[Path]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for input_path in input_paths:
        if not input_path.exists():
            raise FileNotFoundError(f"CSV input not found: {input_path}")
        with input_path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            fieldnames = reader.fieldnames or []
            if "session.code" not in fieldnames or "session.config.name" not in fieldnames:
                raise ValueError(
                    f"{input_path} does not look like an all_apps_wide.csv export. "
                    "Use the oTree all_apps_wide export for grading summaries."
                )
            for row in reader:
                row["__source_file"] = input_path.name
                rows.append(row)
    if not rows:
        raise ValueError("No rows were found in the provided grading inputs.")
    return rows


def percentile_map(items: list[tuple[str, Decimal]]) -> dict[str, float]:
    if not items:
        return {}
    ordered = sorted(items, key=lambda item: item[1])
    if len(ordered) == 1:
        return {ordered[0][0]: 100.0}

    result: dict[str, float] = {}
    index = 0
    while index < len(ordered):
        value = ordered[index][1]
        end = index
        while end + 1 < len(ordered) and ordered[end + 1][1] == value:
            end += 1
        average_rank = (index + 1 + end + 1) / 2
        percentile = 100.0 * (average_rank - 1) / (len(ordered) - 1)
        for position in range(index, end + 1):
            result[ordered[position][0]] = percentile
        index = end + 1
    return result


def load_identifier(row: dict[str, str], *, allow_anonymous: bool) -> str:
    label = ""
    for candidate in LABEL_CANDIDATES:
        label = (row.get(candidate, "") or "").strip()
        if label:
            return label
    if allow_anonymous:
        for candidate in CODE_CANDIDATES:
            code = (row.get(candidate, "") or "").strip()
            if code:
                return f"ANON_{code}"
    source_file = row.get("__source_file", "unknown file")
    raise ValueError(
        f"Missing participant label in {source_file} for session {row.get('session.config.name', '')}. "
        "Use tracked labels or pass --allow-anonymous for a diagnostic-only summary."
    )


def build_session_records(rows: list[dict[str, str]], *, allow_anonymous: bool) -> list[dict[str, object]]:
    unsupported = missing_supported_apps()
    if unsupported:
        raise ValueError("Missing grading support for apps: " + ", ".join(unsupported))

    rows_by_session: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        session_key = (row.get("session.code", ""), row.get("__source_file", ""))
        rows_by_session[session_key].append(row)

    session_records: list[dict[str, object]] = []
    for (_, _), session_rows in rows_by_session.items():
        context = SessionContext.from_rows(session_rows)
        for row in session_rows:
            participant_label = load_identifier(row, allow_anonymous=allow_anonymous)
            opportunities = collect_opportunities(row, context)
            raw_total = sum(opportunity.raw_earnings for opportunity in opportunities)
            app_total = sum(opportunity.app_payoff for opportunity in opportunities)
            max_total = sum(opportunity.max_attainable for opportunity in opportunities)
            active_count = sum(opportunity.active_opportunity for opportunity in opportunities)
            sit_out_count = sum(opportunity.sit_out for opportunity in opportunities)
            attainment = ZERO if max_total == ZERO else raw_total / max_total
            session_records.append(
                dict(
                    participant_label=participant_label,
                    session_code=context.session_code,
                    session_name=context.session_name,
                    raw_earnings_points=raw_total,
                    app_payoff_points=app_total,
                    max_attainable_points=max_total,
                    attainment_fraction=attainment,
                    active_opportunity_count=active_count,
                    sit_out_count=sit_out_count,
                    source_file=";".join(sorted(context.source_files)),
                )
            )
    return session_records


def assign_session_percentiles(session_records: list[dict[str, object]]) -> None:
    by_session: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in session_records:
        by_session[str(record["session_code"])].append(record)

    for records in by_session.values():
        eligible = [
            (str(record["participant_label"]), record["raw_earnings_points"])
            for record in records
            if int(record["active_opportunity_count"]) > 0
        ]
        raw_percentiles = percentile_map(eligible)
        eligible_attainment = [
            (str(record["participant_label"]), record["attainment_fraction"])
            for record in records
            if int(record["active_opportunity_count"]) > 0
        ]
        attainment_percentiles = percentile_map(eligible_attainment)
        for record in records:
            key = str(record["participant_label"])
            record["raw_earnings_percentile"] = raw_percentiles.get(key)
            record["attainment_fraction_percentile"] = attainment_percentiles.get(key)


def build_quarter_records(session_records: list[dict[str, object]]) -> list[dict[str, object]]:
    quarter_records: list[dict[str, object]] = []
    by_participant: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in session_records:
        by_participant[str(record["participant_label"])].append(record)

    for participant_label, records in sorted(by_participant.items()):
        total_raw = sum(record["raw_earnings_points"] for record in records)
        total_app = sum(record["app_payoff_points"] for record in records)
        total_max = sum(record["max_attainable_points"] for record in records)
        active_count = sum(int(record["active_opportunity_count"]) for record in records)
        sit_out_count = sum(int(record["sit_out_count"]) for record in records)
        quarter_records.append(
            dict(
                participant_label=participant_label,
                total_raw_earnings_points=total_raw,
                total_app_payoff_points=total_app,
                total_max_attainable_points=total_max,
                overall_attainment_fraction=ZERO if total_max == ZERO else total_raw / total_max,
                session_count=len(records),
                active_opportunity_count=active_count,
                sit_out_count=sit_out_count,
                sessions=";".join(record["session_name"] for record in records),
            )
        )

    eligible_raw = [
        (str(record["participant_label"]), record["total_raw_earnings_points"])
        for record in quarter_records
        if int(record["active_opportunity_count"]) > 0
    ]
    eligible_attainment = [
        (str(record["participant_label"]), record["overall_attainment_fraction"])
        for record in quarter_records
        if int(record["active_opportunity_count"]) > 0
    ]
    raw_percentiles = percentile_map(eligible_raw)
    attainment_percentiles = percentile_map(eligible_attainment)
    for record in quarter_records:
        key = str(record["participant_label"])
        record["raw_earnings_percentile"] = raw_percentiles.get(key)
        record["attainment_fraction_percentile"] = attainment_percentiles.get(key)
    return quarter_records


def write_session_summary(output_path: Path, session_records: list[dict[str, object]]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "participant_label",
                "session_name",
                "raw_earnings_points",
                "app_payoff_points",
                "max_attainable_points",
                "attainment_fraction",
                "raw_earnings_percentile",
                "attainment_fraction_percentile",
                "active_opportunity_count",
                "sit_out_count",
                "source_file",
            ]
        )
        for record in sorted(session_records, key=lambda entry: (str(entry["session_name"]), str(entry["participant_label"]))):
            writer.writerow(
                [
                    record["participant_label"],
                    record["session_name"],
                    format_decimal(record["raw_earnings_points"]),
                    format_decimal(record["app_payoff_points"]),
                    format_decimal(record["max_attainable_points"]),
                    format_decimal(record["attainment_fraction"]),
                    format_percentile(record.get("raw_earnings_percentile")),
                    format_percentile(record.get("attainment_fraction_percentile")),
                    record["active_opportunity_count"],
                    record["sit_out_count"],
                    record["source_file"],
                ]
            )


def write_quarter_summary(output_path: Path, quarter_records: list[dict[str, object]]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "participant_label",
                "total_raw_earnings_points",
                "total_app_payoff_points",
                "total_max_attainable_points",
                "overall_attainment_fraction",
                "raw_earnings_percentile",
                "attainment_fraction_percentile",
                "session_count",
                "active_opportunity_count",
                "sit_out_count",
                "sessions",
            ]
        )
        for record in quarter_records:
            writer.writerow(
                [
                    record["participant_label"],
                    format_decimal(record["total_raw_earnings_points"]),
                    format_decimal(record["total_app_payoff_points"]),
                    format_decimal(record["total_max_attainable_points"]),
                    format_decimal(record["overall_attainment_fraction"]),
                    format_percentile(record.get("raw_earnings_percentile")),
                    format_percentile(record.get("attainment_fraction_percentile")),
                    record["session_count"],
                    record["active_opportunity_count"],
                    record["sit_out_count"],
                    record["sessions"],
                ]
            )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build per-session and quarter-long grading summaries from oTree all_apps_wide exports."
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        help="all_apps_wide.csv files, export directories, or directories containing export folders.",
    )
    parser.add_argument(
        "--session-output",
        type=Path,
        default=Path("dist/grading/session_summary.csv"),
        help="Output path for the per-session summary.",
    )
    parser.add_argument(
        "--quarter-output",
        type=Path,
        default=Path("dist/grading/quarter_summary.csv"),
        help="Output path for the quarter summary.",
    )
    parser.add_argument(
        "--allow-anonymous",
        action="store_true",
        help="Allow missing participant labels by falling back to participant codes. Diagnostic use only.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    input_paths = resolve_input_paths(args.inputs)
    rows = load_wide_rows(input_paths)
    session_records = build_session_records(rows, allow_anonymous=args.allow_anonymous)
    assign_session_percentiles(session_records)
    quarter_records = build_quarter_records(session_records)
    write_session_summary(args.session_output, session_records)
    write_quarter_summary(args.quarter_output, quarter_records)
    print(f"Wrote session grading summary to {args.session_output}")
    print(f"Wrote quarter grading summary to {args.quarter_output}")


if __name__ == "__main__":
    main()
