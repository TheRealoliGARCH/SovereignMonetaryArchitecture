"""Validation helpers for the BSMPM v0.4 empirical source audit."""
from __future__ import annotations

from typing import Any
import pandas as pd

ROSTER_COLUMNS = (
    "iso3", "country", "imf_wp24_group", "monetary_policy_authority",
    "shock_series_id", "study_window_start", "study_window_end",
)


def validate_country_roster(roster: pd.DataFrame) -> dict[str, Any]:
    """Validate the 29-country IMF WP/24/224 market sample frame.

    The sample contains 29 country markets but only 20 monetary authorities:
    ten euro-area countries share one ECB shock series.
    """
    missing = [column for column in ROSTER_COLUMNS if column not in roster.columns]
    if missing:
        raise ValueError(f"missing roster columns: {missing}")
    frame = roster.loc[:, ROSTER_COLUMNS].copy()
    if frame.empty:
        raise ValueError("country roster cannot be empty")
    for column in ROSTER_COLUMNS:
        frame[column] = frame[column].astype("string").fillna("").str.strip()
        if frame[column].eq("").any():
            raise ValueError(f"roster field {column} cannot be blank")
    if frame["iso3"].str.fullmatch(r"[A-Z]{3}").eq(False).any():
        raise ValueError("iso3 codes must contain exactly three uppercase letters")
    if frame["iso3"].duplicated().any():
        raise ValueError("ISO3 country codes must be unique")
    if not frame["imf_wp24_group"].isin(["AE", "EM"]).all():
        raise ValueError("imf_wp24_group must be AE or EM")
    if frame["shock_sample_start"].gt(frame["shock_sample_end"]).any():
        raise ValueError("study window start must not exceed end")
    return {
        "countries": int(len(frame)),
        "advanced_economies": int(frame["imf_wp24_group"].eq("AE").sum()),
        "emerging_markets": int(frame["imf_wp24_group"].eq("EM").sum()),
        "monetary_authorities": int(frame["monetary_policy_authority"].nunique()),
        "shock_series": int(frame["shock_series_id"].nunique()),
        "shared_euro_area_markets": int(frame["shock_series_id"].eq("ECB_1Y_OIS").sum()),
    }
