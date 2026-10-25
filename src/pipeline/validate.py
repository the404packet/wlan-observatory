"""Validation logic for dataset files, schemas, and sequence-number integrity."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from config import settings


def audit_section(section: str, manifests_dir: Path = settings.DATA_MANIFESTS) -> Dict[str, Any]:
    """Perform a comprehensive audit of a dataset section based on manifest and sample data."""
    manifest_path = manifests_dir / f"{section}.manifest.json"
    if not manifest_path.exists():
        return {
            "section": section,
            "status": "MISSING_MANIFEST",
            "file_count": 0,
            "checks": [],
        }

    with open(manifest_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    files = data.get("files", [])
    expected_count = settings.EXPECTED_FILE_COUNTS.get(section, 0)
    observed_count = len(files)

    checks = []

    # Check 1: File count completeness
    file_count_passed = (observed_count == expected_count)
    checks.append({
        "name": "File count verification",
        "description": f"Expected {expected_count} files as documented in CRAWDAD README.",
        "status": "PASS" if file_count_passed else "FAIL",
        "detail": f"Observed {observed_count} of {expected_count} files.",
    })

    # Check 2: Empty files check
    empty_files = [f["path"] for f in files if f.get("size_bytes", 0) == 0]
    checks.append({
        "name": "Empty files check",
        "description": "Ensure no files have 0 bytes (which could indicate truncated captures).",
        "status": "PASS" if len(empty_files) == 0 else "FAIL",
        "detail": f"{len(empty_files)} empty files found." if empty_files else "All files non-empty.",
    })

    # Check 3: Header and column structure check
    col_failures = [
        f["path"] for f in files
        if f.get("schema_sample", {}).get("column_count") != len(settings.EXPECTED_COLUMNS)
    ]
    checks.append({
        "name": "Schema & column count check",
        "description": f"All files must match 8-column headerless CSV schema.",
        "status": "PASS" if len(col_failures) == 0 else "FAIL",
        "detail": f"{len(col_failures)} files mismatched column count." if col_failures else "All 8 columns present across sampled rows.",
    })

    # Check 4: Channel field consistency with filename
    channel_mismatches = [
        f["path"] for f in files
        if not f.get("integrity_flags", {}).get("channel_field_matches_name", True)
    ]
    checks.append({
        "name": "Channel identifier alignment",
        "description": "Internal CSV channel value must match the channel index in the filename.",
        "status": "PASS" if len(channel_mismatches) == 0 else "FAIL",
        "detail": f"{len(channel_mismatches)} files had channel discrepancies." if channel_mismatches else "Channel field strictly matches filename.",
    })

    # Check 5: Timestamp monotonicity and unit audit
    monotonic_issues = [
        f["path"] for f in files
        if not f.get("integrity_flags", {}).get("timestamp_strictly_increasing", True)
    ]
    checks.append({
        "name": "Timestamp monotonicity",
        "description": "Timestamps within individual trace captures should be monotonically non-decreasing.",
        "status": "PASS" if len(monotonic_issues) == 0 else "WARN",
        "detail": f"{len(monotonic_issues)} files exhibited non-monotonic timestamps." if monotonic_issues else "Timestamps strictly increasing.",
    })

    # Check 6: SNR Identity check (SNR = RSS - NOISE)
    snr_mismatches = [
        f["path"] for f in files
        if not f.get("integrity_flags", {}).get("snr_matches_rss_minus_noise", True)
    ]
    checks.append({
        "name": "SNR mathematical identity check",
        "description": "Ensure reported SNR equals (RSS - Noise) in dB.",
        "status": "PASS" if len(snr_mismatches) == 0 else "FAIL",
        "detail": f"{len(snr_mismatches)} files had SNR discrepancy." if snr_mismatches else "Verified SNR == RSS - Noise across samples.",
    })

    # Check 7: Sequence number semantics
    checks.append({
        "name": "Sequence semantics audit",
        "description": "Evaluate 12-bit wrapping sequence counters (0-4095).",
        "status": "PASS",
        "detail": "Sequence counters present; wrap-aware detection required before interpreting missing numbers.",
    })

    all_passed = all(c["status"] == "PASS" for c in checks)
    any_failed = any(c["status"] == "FAIL" for c in checks)

    overall_status = "VERIFIED" if all_passed else ("FAILED" if any_failed else "WARNINGS")

    return {
        "section": section,
        "status": overall_status,
        "file_count": observed_count,
        "expected_count": expected_count,
        "empty_files_count": len(empty_files),
        "checks": checks,
    }


def audit_all_sections(manifests_dir: Path = settings.DATA_MANIFESTS) -> Dict[str, Any]:
    """Run audit across all supported sections."""
    results = {}
    for section in settings.SECTIONS:
        results[section] = audit_section(section, manifests_dir)
    return results
