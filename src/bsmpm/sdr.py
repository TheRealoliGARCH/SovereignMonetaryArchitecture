"""SDR exposure metrics for the BSMPM empirical architecture.

The module transforms user-supplied, source-documented country-period data.
It does not retrieve SDR data, infer missing observations, or establish that
SDR participation causally constrains national monetary policy.
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

KEY_COLUMNS = ("iso3", "period")
REQUIRED_STOCK_COLUMNS = (
    "sdr_cumulative_allocations_usd",
    "sdr_holdings_usd",
    "fx_reserves_usd",
    "gdp_usd",
)
OPTIONAL_NUMERIC_COLUMNS = (
    "exchange_rate_lcu_per_usd",
    "sdr_consistent_exchange_rate_lcu_per_usd",
    "sdr_allocation_lcu",
    "policy_rate_pct",
    "reserve_remuneration_rate_pct",
)


def validate_sdr_panel(data: pd.DataFrame) -> dict[str, Any]:
    """Validate a country-period SDR exposure dataset.

    Required stock values are nonnegative USD amounts. FX reserves and GDP
    must be strictly positive for ratio construction. Optional rate and FX
    fields may be missing, but observed values must be finite. Exchange rates
    must be positive and use the same local-currency-per-USD quotation.
    """
    required = [*KEY_COLUMNS, *REQUIRED_STOCK_COLUMNS]
    missing = [name for name in required if name not in data.columns]
    if missing:
        raise ValueError(f"missing required SDR panel columns: {missing}")
    frame = data.loc[:, list(dict.fromkeys(required + [
        name for name in OPTIONAL_NUMERIC_COLUMNS if name in data.columns
    ]))].copy()
    if frame.empty:
        raise ValueError("SDR panel cannot be empty")
    for column in KEY_COLUMNS:
        frame[column] = frame[column].astype("string").fillna("").str.strip()
        if frame[column].eq("").any():
            raise ValueError(f"{column} identifiers cannot be blank")
    if frame["iso3"].str.fullmatch(r"[A-Z]{3}").eq(False).any():
        raise ValueError("iso3 must contain exactly three uppercase letters")
    if frame.duplicated(list(KEY_COLUMNS)).any():
        raise ValueError("country-period observations must be unique")

    numeric_columns = [*REQUIRED_STOCK_COLUMNS, *[
        name for name in OPTIONAL_NUMERIC_COLUMNS if name in frame.columns
    ]]
    for column in numeric_columns:
        original = frame[column]
        converted = pd.to_numeric(original, errors="coerce")
        invalid = original.notna() & original.astype(str).str.strip().ne("") & converted.isna()
        if invalid.any():
            raise ValueError(f"{column} contains nonnumeric values")
        observed = converted.dropna().to_numpy(dtype=float)
        if not np.isfinite(observed).all():
            raise ValueError(f"{column} must contain finite values")
        frame[column] = converted

    for column in REQUIRED_STOCK_COLUMNS:
        if frame[column].isna().any():
            raise ValueError(f"{column} cannot be missing")
        if frame[column].lt(0).any():
            raise ValueError(f"{column} must be nonnegative")
    for column in ("fx_reserves_usd", "gdp_usd"):
        if frame[column].le(0).any():
            raise ValueError(f"{column} must be strictly positive")
    if "sdr_allocation_lcu" in frame.columns and frame["sdr_allocation_lcu"].dropna().lt(0).any():
        raise ValueError("sdr_allocation_lcu must be nonnegative where observed")
    for column in (
        "exchange_rate_lcu_per_usd",
        "sdr_consistent_exchange_rate_lcu_per_usd",
    ):
        if column in frame.columns and frame[column].dropna().le(0).any():
            raise ValueError(f"{column} must be positive where observed")

    return {
        "rows": int(len(frame)),
        "countries": int(frame["iso3"].nunique()),
        "periods": int(frame["period"].nunique()),
        "optional_fields_present": [
            name for name in OPTIONAL_NUMERIC_COLUMNS if name in frame.columns
        ],
        "missing_optional": {
            name: int(frame[name].isna().sum())
            for name in OPTIONAL_NUMERIC_COLUMNS if name in frame.columns
        },
    }


def construct_sdr_exposure_metrics(data: pd.DataFrame) -> pd.DataFrame:
    """Return validated SDR ratios and optional FX/sterilization measures.

    Definitions:
    - allocation_to_gdp: cumulative SDR allocations / nominal GDP;
    - holdings_to_reserves: SDR holdings / total FX reserves;
    - holdings_minus_allocations_usd: holdings less cumulative allocations;
    - sdr_fx_deviation_log: log(actual FX quote / SDR-consistent FX quote);
    - sdr_sterilization_cost_lcu: (policy rate - reserve remuneration rate)
      times period SDR allocation, with rates converted from percent to units.

    The holdings-minus-allocations measure is a descriptive stock comparison;
    it is not asserted to equal a complete IMF net-position accounting measure.
    """
    validate_sdr_panel(data)
    frame = data.copy()
    for column in REQUIRED_STOCK_COLUMNS:
        frame[column] = pd.to_numeric(frame[column], errors="raise")
    frame["sdr_allocation_to_gdp"] = (
        frame["sdr_cumulative_allocations_usd"] / frame["gdp_usd"]
    )
    frame["sdr_holdings_to_fx_reserves"] = (
        frame["sdr_holdings_usd"] / frame["fx_reserves_usd"]
    )
    frame["sdr_holdings_minus_cumulative_allocations_usd"] = (
        frame["sdr_holdings_usd"] - frame["sdr_cumulative_allocations_usd"]
    )

    fx_actual = "exchange_rate_lcu_per_usd"
    fx_benchmark = "sdr_consistent_exchange_rate_lcu_per_usd"
    if fx_actual in frame.columns and fx_benchmark in frame.columns:
        actual = pd.to_numeric(frame[fx_actual], errors="coerce")
        benchmark = pd.to_numeric(frame[fx_benchmark], errors="coerce")
        frame["sdr_fx_deviation_log"] = np.log(actual / benchmark)

    sterilization_columns = {
        "sdr_allocation_lcu", "policy_rate_pct", "reserve_remuneration_rate_pct"
    }
    if sterilization_columns.issubset(frame.columns):
        allocation = pd.to_numeric(frame["sdr_allocation_lcu"], errors="coerce")
        policy = pd.to_numeric(frame["policy_rate_pct"], errors="coerce")
        remuneration = pd.to_numeric(
            frame["reserve_remuneration_rate_pct"], errors="coerce"
        )
        frame["sdr_sterilization_cost_lcu"] = (
            (policy - remuneration) / 100.0
        ) * allocation
    return frame
