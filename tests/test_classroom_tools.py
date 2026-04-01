from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

from payment_info import PaymentInfo
from scripts.audit_headcount_matrix import ROOT_DIR as PROJECT_ROOT
from scripts.build_quarter_earnings import aggregate_earnings, write_summary
from scripts.generate_room_labels import generate_labels, write_labels


def test_generate_room_labels_default_format(tmp_path):
    output_path = tmp_path / "econ101.txt"
    labels = generate_labels("ECON101", count=3)
    write_labels(output_path, labels)
    assert output_path.read_text(encoding="utf-8").splitlines() == [
        "ECON101_001",
        "ECON101_002",
        "ECON101_003",
    ]


def test_build_quarter_earnings_aggregates_multiple_files(tmp_path):
    week_one = tmp_path / "week01.csv"
    week_two = tmp_path / "week02.csv"

    with week_one.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["participant.label", "session_config_name", "payoff"])
        writer.writeheader()
        writer.writerow(
            {
                "participant.label": "ECON101_001",
                "session_config_name": "trust",
                "payoff": "15",
            }
        )
        writer.writerow(
            {
                "participant.label": "ECON101_002",
                "session_config_name": "trust",
                "payoff": "10",
            }
        )

    with week_two.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["participant.label", "session_config_name", "payoff"])
        writer.writeheader()
        writer.writerow(
            {
                "participant.label": "ECON101_001",
                "session_config_name": "public_goods",
                "payoff": "5",
            }
        )

    aggregated = aggregate_earnings([week_one, week_two])
    output_path = tmp_path / "quarter.csv"
    write_summary(output_path, aggregated)

    rows = list(csv.DictReader(output_path.open(encoding="utf-8")))
    assert rows == [
        {
            "participant_label": "ECON101_001",
            "total_points": "20",
            "session_count": "2",
            "row_count": "2",
            "sessions": "public_goods;trust",
            "source_files": "week01.csv;week02.csv",
        },
        {
            "participant_label": "ECON101_002",
            "total_points": "10",
            "session_count": "1",
            "row_count": "1",
            "sessions": "trust",
            "source_files": "week01.csv",
        },
    ]


def test_payment_info_prefers_participant_label():
    player = SimpleNamespace(participant=SimpleNamespace(label="ECON101_001", code="abc123"))
    assert PaymentInfo.vars_for_template(player)["redemption_code"] == "ECON101_001"


def test_payment_info_falls_back_to_participant_code():
    player = SimpleNamespace(participant=SimpleNamespace(label="", code="abc123"))
    assert PaymentInfo.vars_for_template(player)["redemption_code"] == "abc123"


def test_headcount_audit_script_passes():
    subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts" / "audit_headcount_matrix.py")],
        cwd=PROJECT_ROOT,
        check=True,
    )
