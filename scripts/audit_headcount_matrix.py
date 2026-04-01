from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
DOC_PATH = ROOT_DIR / "docs" / "headcount-and-fallbacks.md"

EXPECTED_ODD_BEHAVIOR = {
    "any count": "not applicable",
    "odd-count resilient": "strategy fallback",
    "exact multiple of 2": "skip unmatched",
    "exact multiple of 3": "skip unmatched",
    "exact multiple of 4": "skip unmatched",
    "exact multiple of 8": "skip unmatched",
}


def load_matrix(doc_path: Path) -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    table_headers = None
    for raw_line in doc_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if not cells or set(cells[0]) == {"-"}:
            continue
        if cells[0] == "App":
            table_headers = cells
            continue
        if not table_headers or not cells[0].startswith("`"):
            continue
        app_name = cells[0].strip("`")
        rows[app_name] = dict(zip(table_headers[1:], cells[1:]))
    if not rows:
        raise ValueError(f"No headcount rows found in {doc_path}")
    return rows


def load_app_metadata(root_dir: Path) -> dict[str, dict[str, object]]:
    metadata: dict[str, dict[str, object]] = {}
    sys.path.insert(0, str(root_dir))
    for init_path in sorted(root_dir.glob("*/__init__.py")):
        app_name = init_path.parent.name
        source_text = init_path.read_text(encoding="utf-8")
        spec = importlib.util.spec_from_file_location(f"headcount_audit_{app_name}", init_path)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        group_size = module.C.PLAYERS_PER_GROUP
        metadata[app_name] = dict(
            group_size=group_size,
            strategy_fallback="force_strategy" in source_text,
        )
    return metadata


def expected_group_size_label(group_size: object) -> str:
    if group_size is None:
        return "ungrouped"
    return str(group_size)


def expected_minimum(group_size: object, strategy_fallback: bool) -> str:
    if group_size in (None, 1):
        return "1"
    if strategy_fallback:
        return "2"
    return str(group_size)


def expected_compatibility(group_size: object, strategy_fallback: bool) -> str:
    if group_size in (None, 1):
        return "any count"
    if strategy_fallback:
        return "odd-count resilient"
    return f"exact multiple of {group_size}"


def validate_matrix(rows: dict[str, dict[str, str]], metadata: dict[str, dict[str, object]]) -> None:
    documented = set(rows)
    actual = set(metadata)
    missing_docs = sorted(actual - documented)
    extra_docs = sorted(documented - actual)
    errors: list[str] = []

    if missing_docs:
        errors.append(f"Missing apps in headcount matrix: {', '.join(missing_docs)}")
    if extra_docs:
        errors.append(f"Unknown apps in headcount matrix: {', '.join(extra_docs)}")

    for app_name in sorted(actual & documented):
        row = rows[app_name]
        group_size = metadata[app_name]["group_size"]
        strategy_fallback = metadata[app_name]["strategy_fallback"]

        expected_group = expected_group_size_label(group_size)
        expected_min = expected_minimum(group_size, strategy_fallback)
        expected_compat = expected_compatibility(group_size, strategy_fallback)
        expected_odd = EXPECTED_ODD_BEHAVIOR[expected_compat]

        if row["Group size"] != expected_group:
            errors.append(
                f"{app_name}: expected group size '{expected_group}' but found '{row['Group size']}'"
            )
        if row["Minimum workable headcount"] != expected_min:
            errors.append(
                f"{app_name}: expected minimum headcount '{expected_min}' but found '{row['Minimum workable headcount']}'"
            )
        if row["Compatibility"] != expected_compat:
            errors.append(
                f"{app_name}: expected compatibility '{expected_compat}' but found '{row['Compatibility']}'"
            )
        if row["Odd-count behavior"] != expected_odd:
            errors.append(
                f"{app_name}: expected odd-count behavior '{expected_odd}' but found '{row['Odd-count behavior']}'"
            )

    guess_notes = rows.get("ae_guess_two_thirds", {}).get("Notes", "").lower()
    if "pair" not in guess_notes:
        errors.append("ae_guess_two_thirds: notes should warn that the current implementation is paired.")

    if errors:
        raise ValueError("\n".join(errors))


def main() -> None:
    rows = load_matrix(DOC_PATH)
    metadata = load_app_metadata(ROOT_DIR)
    validate_matrix(rows, metadata)
    print(f"Verified headcount matrix for {len(rows)} apps.")


if __name__ == "__main__":
    main()
