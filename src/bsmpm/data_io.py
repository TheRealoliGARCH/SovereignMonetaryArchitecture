"""Reproducible ingestion and provenance utilities for BSMPM empirical data.

This module validates user-supplied country-period CSVs. It does not download,
scrape, or fabricate observations and does not certify the validity of sources.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd

PANEL_COLUMNS = ("country", "period", "outcome", "policy_shock", "btc_use_share")
NUMERIC_COLUMNS = ("outcome", "policy_shock", "btc_use_share")
SOURCE_COLUMNS = (
    "source_id", "variable", "provider", "url", "definition", "unit",
    "frequency", "coverage", "retrieval_date", "license", "transformation", "status",
)


def validate_empirical_dataset(data: pd.DataFrame) -> dict[str, Any]:
    """Validate panel structure; retain and count missing numeric observations."""
    missing_columns = [name for name in PANEL_COLUMNS if name not in data.columns]
    if missing_columns:
        raise ValueError(f"missing required panel columns: {missing_columns}")
    frame = data.loc[:, PANEL_COLUMNS].copy()
    if frame["country"].isna().any() or frame["period"].isna().any():
        raise ValueError("country and period identifiers cannot be missing")
    for key in ("country", "period"):
        frame[key] = frame[key].astype(str).str.strip()
        if frame[key].eq("").any():
            raise ValueError(f"{key} identifiers cannot be blank")
    if frame.duplicated(["country", "period"]).any():
        raise ValueError("country-period observations must be unique")
    missing_counts = {}
    for column in NUMERIC_COLUMNS:
        original = frame[column]
        converted = pd.to_numeric(original, errors="coerce")
        invalid = original.notna() & original.astype(str).str.strip().ne("") & converted.isna()
        if invalid.any():
            raise ValueError(f"{column} contains nonnumeric values")
        frame[column] = converted
        observed = frame[column].dropna().to_numpy(dtype=float)
        if not all(abs(value) != float("inf") for value in observed):
            raise ValueError(f"{column} must contain only finite values")
        missing_counts[column] = int(frame[column].isna().sum())
    observed_share = frame["btc_use_share"].dropna()
    if not observed_share.between(0.0, 1.0).all():
        raise ValueError("btc_use_share must lie in [0, 1] where observed")
    if frame.empty:
        raise ValueError("dataset must contain at least one row")
    return {
        "rows": int(len(frame)),
        "countries": int(frame["country"].nunique()),
        "periods": int(frame["period"].nunique()),
        "missing_numeric": missing_counts,
        "columns": list(PANEL_COLUMNS),
    }


def load_country_panel(path: str | Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Load a UTF-8 CSV and validate its BSMPM panel structure."""
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(source)
    frame = pd.read_csv(source, encoding="utf-8")
    return frame, validate_empirical_dataset(frame)


def validate_source_registry(registry: pd.DataFrame) -> dict[str, Any]:
    """Validate series metadata; source URLs are recorded, not fetched."""
    missing = [name for name in SOURCE_COLUMNS if name not in registry.columns]
    if missing:
        raise ValueError(f"missing source-registry columns: {missing}")
    frame = registry.loc[:, SOURCE_COLUMNS].copy()
    if frame.empty:
        raise ValueError("source registry must contain at least one record")
    for column in SOURCE_COLUMNS:
        frame[column] = frame[column].fillna("").astype(str).str.strip()
        if frame[column].eq("").any():
            raise ValueError(f"source-registry field {column} cannot be blank")
    if frame.duplicated(["source_id", "variable"]).any():
        raise ValueError("source_id-variable pairs must be unique")
    if (~frame["url"].str.startswith(("https://", "http://"))).any():
        raise ValueError("source URLs must use http:// or https://")
    for value in frame["retrieval_date"]:
        try:
            date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError("retrieval_date must use ISO YYYY-MM-DD format") from exc
    return {"records": int(len(frame)), "variables": sorted(frame["variable"].unique().tolist())}


def build_provenance_manifest(
    dataset_path: str | Path, *, source_registry_path: str | Path,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a manifest with file hashes and structural validation summaries."""
    dataset, registry_path = Path(dataset_path), Path(source_registry_path)
    if not dataset.is_file() or not registry_path.is_file():
        raise FileNotFoundError("dataset and source registry files must both exist")
    _, panel_summary = load_country_panel(dataset)
    registry_summary = validate_source_registry(pd.read_csv(registry_path, encoding="utf-8"))

    def sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    return {
        "manifest_version": "1.0",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset": {"file": dataset.name, "sha256": sha256(dataset), **panel_summary},
        "source_registry": {
            "file": registry_path.name, "sha256": sha256(registry_path), **registry_summary,
        },
        "metadata": metadata or {},
        "notice": (
            "Hashes establish file identity, not source authenticity, licensing "
            "compliance, measurement validity, or causal identification."
        ),
    }


def write_provenance_manifest(
    dataset_path: str | Path, *, source_registry_path: str | Path,
    output_path: str | Path, metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Write a JSON provenance manifest and return its contents."""
    manifest = build_provenance_manifest(
        dataset_path, source_registry_path=source_registry_path, metadata=metadata
    )
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest
