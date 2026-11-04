"""Reproducible local data assembly with explicit provenance.

No network retrieval is performed. Raw files must be acquired under the user's
source access and licensing conditions and supplied as local CSV files.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping, Sequence

import pandas as pd


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_documented_csv(
    path: str | Path,
    *,
    source_id: str,
    source_name: str,
    source_url: str,
    access_date: str,
    license_status: str,
    required_columns: Sequence[str],
) -> tuple[pd.DataFrame, dict]:
    """Load a local CSV and return data plus a verifiable provenance record."""
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(file_path)
    metadata = {
        "source_id": source_id, "source_name": source_name,
        "source_url": source_url, "access_date": access_date,
        "license_status": license_status,
    }
    if any(not isinstance(value, str) or not value.strip() for value in metadata.values()):
        raise ValueError("source identity, URL, access date, and license status are required")
    if not source_url.startswith(("https://", "http://")):
        raise ValueError("source_url must use http:// or https://")
    from datetime import date
    try:
        date.fromisoformat(access_date)
    except ValueError as exc:
        raise ValueError("access_date must use ISO YYYY-MM-DD format") from exc
    if not required_columns or any(not isinstance(column, str) or not column for column in required_columns):
        raise ValueError("required_columns must contain nonempty column names")
    frame = pd.read_csv(file_path, encoding="utf-8")
    if frame.empty:
        raise ValueError("source CSV must contain at least one observation")
    missing = [column for column in required_columns if column not in frame.columns]
    if missing:
        raise ValueError(f"{file_path.name} is missing required columns: {missing}")
    record = {
        "source_id": source_id,
        "source_name": source_name,
        "source_url": source_url,
        "access_date": access_date,
        "license_status": license_status,
        "local_filename": file_path.name,
        "sha256": sha256_file(file_path),
        "rows": int(len(frame)),
        "columns": list(frame.columns),
    }
    return frame, record


def merge_country_period_sources(
    sources: Mapping[str, pd.DataFrame],
    *,
    keys: Sequence[str] = ("iso3", "period"),
    how: str = "inner",
) -> pd.DataFrame:
    """Merge country-period source tables without temporal interpolation.

    Each source must have unique, nonmissing keys. Overlapping non-key column
    names are rejected to prevent silent suffixing or ambiguous provenance.
    """
    if not sources:
        raise ValueError("at least one source table is required")
    if not keys or len(set(keys)) != len(keys) or any(not isinstance(key, str) or not key for key in keys):
        raise ValueError("keys must contain unique, nonempty column names")
    if how not in {"inner", "left", "outer"}:
        raise ValueError("how must be inner, left, or outer")
    merged = None
    used_columns = set(keys)
    for source_name, frame in sources.items():
        missing = [key for key in keys if key not in frame.columns]
        if missing:
            raise ValueError(f"source {source_name} missing merge keys: {missing}")
        if frame[list(keys)].isna().any().any():
            raise ValueError(f"source {source_name} has missing merge keys")
        if frame.duplicated(list(keys)).any():
            raise ValueError(f"source {source_name} has duplicate merge keys")
        overlaps = (set(frame.columns) - set(keys)) & used_columns
        if overlaps:
            raise ValueError(f"source {source_name} has ambiguous overlapping columns: {sorted(overlaps)}")
        used_columns.update(set(frame.columns) - set(keys))
        if merged is None:
            merged = frame.copy()
        else:
            merged = merged.merge(frame, on=list(keys), how=how, validate="one_to_one")
    return merged.sort_values(list(keys)).reset_index(drop=True)


def write_acquisition_manifest(records: Sequence[dict], output_path: str | Path) -> Path:
    """Write a JSON manifest; hashes identify files but do not prove validity."""
    if not records:
        raise ValueError("at least one source record is required")
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "manifest_version": "1.0",
        "source_count": len(records),
        "sources": list(records),
        "limitations": [
            "A SHA-256 hash establishes file identity, not source authenticity.",
            "License status is user-supplied and requires independent review.",
            "No network retrieval, interpolation, or imputation is performed.",
        ],
    }
    destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return destination
