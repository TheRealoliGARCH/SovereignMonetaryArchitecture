"""Transparent, researcher-weighted sovereign monetary autonomy index."""
from __future__ import annotations

from collections.abc import Mapping, Sequence

import numpy as np
import pandas as pd

DEFAULT_DIRECTIONS = {
    "domestic_monetary_control": 1,
    "exchange_rate_flexibility": 1,
    "reserve_adequacy": 1,
    "sdr_exposure": -1,
}


def construct_monetary_autonomy_index(
    data: pd.DataFrame,
    *,
    weights: Mapping[str, float],
    directions: Mapping[str, int] | None = None,
    keys: Sequence[str] = ("iso3", "period"),
    output_column: str = "monetary_autonomy_index",
) -> pd.DataFrame:
    """Construct a 0–1 weighted index with explicit polarity and complete data.

    Every component must already be normalized to [0,1]. A direction of +1
    means higher values increase the autonomy score; -1 means higher values
    reduce it. No sample-dependent min-max scaling or missing-value
    renormalization is performed. Bitcoin monetary-use share is deliberately
    not assigned a default normative direction; include it only with an
    explicit researcher-specified weight and polarity.
    """
    if not weights:
        raise ValueError("at least one component weight is required")
    if any(not np.isfinite(float(w)) or float(w) < 0 for w in weights.values()):
        raise ValueError("weights must be finite and nonnegative")
    total_weight = float(sum(weights.values()))
    if not np.isclose(total_weight, 1.0, atol=1e-8):
        raise ValueError("component weights must sum to 1")
    components = list(weights)
    if any(not isinstance(name, str) or not name for name in components):
        raise ValueError("component names must be nonempty strings")
    required = [*keys, *components]
    missing = [name for name in required if name not in data.columns]
    if missing:
        raise ValueError(f"missing autonomy-index columns: {missing}")
    frame = data.copy()
    if frame[list(keys)].isna().any().any() or frame.duplicated(list(keys)).any():
        raise ValueError("index keys must be nonmissing and unique")
    polarity = dict(DEFAULT_DIRECTIONS)
    if directions is not None:
        polarity.update(directions)
    absent = [name for name in components if name not in polarity]
    if absent:
        raise ValueError(f"explicit directions required for components: {absent}")
    if any(polarity[name] not in (-1, 1) for name in components):
        raise ValueError("component directions must be +1 or -1")

    score_columns = []
    for component in components:
        values = pd.to_numeric(frame[component], errors="coerce")
        if values.isna().any() or not np.isfinite(values.to_numpy(dtype=float)).all():
            raise ValueError(f"{component} must be complete and finite")
        if not values.between(0, 1).all():
            raise ValueError(f"{component} must already be normalized to [0, 1]")
        score_name = f"{component}_autonomy_score"
        frame[score_name] = values if polarity[component] == 1 else 1.0 - values
        score_columns.append(score_name)
    frame[output_column] = sum(
        float(weights[name]) * frame[f"{name}_autonomy_score"]
        for name in components
    )
    frame.attrs["index_metadata"] = {
        "weights": {name: float(weights[name]) for name in components},
        "directions": {name: int(polarity[name]) for name in components},
        "scale": [0.0, 1.0],
        "missing_policy": "complete case; no weight renormalization",
        "interpretation": "researcher-defined composite, not an objective or causal measure",
    }
    return frame
