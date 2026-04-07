from __future__ import annotations

import subprocess
import sys

from scripts.audit_instructor_docs import ROOT_DIR as PROJECT_ROOT
from scripts.instructor_docs import load_manifest, ordered_pdf_names


def test_manifest_orders_docs_numerically():
    docs = load_manifest()
    assert [doc.order for doc in docs] == list(range(1, len(docs) + 1))
    assert ordered_pdf_names() == [
        "01_install_from_scratch.pdf",
        "02_instructor_quickstart.pdf",
        "03_hosting_and_deployment.pdf",
        "04_identity_and_grading.pdf",
        "05_classroom_readiness.pdf",
        "06_experiment_catalog.pdf",
        "07_headcount_and_fallbacks.pdf",
        "08_instructor_runbook.pdf",
        "09_data_and_export.pdf",
        "10_troubleshooting.pdf",
    ]


def test_instructor_doc_audit_script_passes():
    subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts" / "audit_instructor_docs.py")],
        cwd=PROJECT_ROOT,
        check=True,
    )
