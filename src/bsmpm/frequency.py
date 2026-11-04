"""Authority-level shock aggregation and country-panel alignment.

Event shocks are aggregated within monetary-authority periods before being
mapped to country markets. This avoids treating duplicated common-authority
shocks as independent country-level policy innovations.
"""
from __future__ import annotations

from collections.abc import Sequence

import pandas as pd


def aggregate_event_shocks(
    events: pd.DataFrame,
    *,
    datetime_column: str = "announcement_datetime_utc",
    authority: str = "monetary_policy_authority",
    shock_series: str = "shock_series_id",
    shock_columns: Sequence[str] = ("epsilon_mp_bp", "epsilon_cbi_bp"),
    frequency: str = "M",
) -> pd.DataFrame:
    """Aggregate event-level basis-point shocks to authority-month or quarter.

    Shock columns are summed within an authority/series/period. Event counts
    are retained, and periods with no events are not implicitly filled with 0.
    """
    if frequency not in {"M", "Q"}:
        raise ValueError("frequency must be 'M' (monthly) or 'Q' (quarterly)")
    required = [datetime_column, authority, shock_series, *shock_columns]
    missing = [name for name in required if name not in events.columns]
    if missing:
        raise ValueError(f"missing required event columns: {missing}")
    frame = events.loc[:, required].copy()
    if frame.empty:
        raise ValueError("event data cannot be empty")
    if frame[[datetime_column, authority, shock_series]].isna().any().any():
        raise ValueError("event timestamps, authorities, and series IDs cannot be missing")
    frame[datetime_column] = pd.to_datetime(frame[datetime_column], utc=True, errors="coerce")
    if frame[datetime_column].isna().any():
        raise ValueError("event timestamps must be valid datetimes")
    for column in shock_columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
        if frame[column].isna().any() or not frame[column].map(lambda x: pd.notna(x) and abs(x) != float("inf")).all():
            raise ValueError(f"{column} must contain finite numeric shocks")
    frame["period"] = frame[datetime_column].dt.to_period(frequency).astype(str)
    keys = [authority, shock_series, "period"]
    result = frame.groupby(keys, as_index=False, sort=True).agg(
        **{column: (column, "sum") for column in shock_columns},
        event_count=(datetime_column, "size"),
    )
    return result


def attach_authority_shocks(
    country_panel: pd.DataFrame,
    roster: pd.DataFrame,
    authority_shocks: pd.DataFrame,
    *,
    country: str = "country",
    period: str = "period",
    authority: str = "monetary_policy_authority",
    shock_series: str = "shock_series_id",
) -> pd.DataFrame:
    """Map one authority-period shock record to each country-period row.

    The roster must map each country to exactly one authority and shock series.
    The authority-shock table must be unique on authority, series, and period.
    Unmatched country-period rows are rejected rather than silently imputed.
    """
    for label, frame, cols in (
        ("country panel", country_panel, [country, period]),
        ("roster", roster, [country, authority, shock_series]),
        ("authority shocks", authority_shocks, [authority, shock_series, period]),
    ):
        missing = [name for name in cols if name not in frame.columns]
        if missing:
            raise ValueError(f"{label} missing required columns: {missing}")
    if country_panel.duplicated([country, period]).any():
        raise ValueError("country-period observations must be unique")
    if roster.duplicated([country]).any():
        raise ValueError("roster must contain one authority mapping per country")
    shock_key = [authority, shock_series, period]
    if authority_shocks.duplicated(shock_key).any():
        raise ValueError("authority shock records must be unique by authority, series, and period")
    mapping = roster.loc[:, [country, authority, shock_series]]
    merged = country_panel.merge(mapping, on=country, how="left", validate="many_to_one")
    if merged[[authority, shock_series]].isna().any().any():
        raise ValueError("every panel country must have a roster authority and shock-series mapping")
    out = merged.merge(
        authority_shocks, on=shock_key, how="left",
        validate="many_to_one", indicator=True,
    )
    if out["_merge"].ne("both").any():
        missing_rows = int(out["_merge"].ne("both").sum())
        raise ValueError(f"{missing_rows} country-period rows lack an authority-period shock")
    return out.drop(columns="_merge")
