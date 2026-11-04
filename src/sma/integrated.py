"""Integrated monetary-policy transmission design.

This layer composes existing country-panel, authority, adoption, and SDR
variables. It does not fetch data or supply an identification strategy.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import pandas as pd

from .empirical import PanelEstimate, estimate_transmission_panel


@dataclass(frozen=True)
class IntegratedTransmissionResult:
    estimate: PanelEstimate
    specification: str
    interaction_terms: tuple[str, ...]
    cluster_variable: str


def prepare_integrated_panel(
    data: pd.DataFrame,
    *,
    shock: str = "policy_shock",
    bitcoin_use: str = "btc_use_share",
    sdr_exposure: str = "sdr_exposure",
) -> pd.DataFrame:
    """Create prespecified two-way and three-way interaction regressors.

    All three input variables must be observed numeric quantities on compatible
    period definitions. Bitcoin use is a monetary-use share, not ownership.
    SDR exposure must be selected and documented by the researcher.
    """
    required = [shock, bitcoin_use, sdr_exposure]
    missing = [column for column in required if column not in data.columns]
    if missing:
        raise ValueError(f"missing integrated-transmission columns: {missing}")
    frame = data.copy()
    for column in required:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    observed = frame[required].dropna()
    if observed.empty:
        raise ValueError("no complete observations for integrated interactions")
    if not __import__("numpy").isfinite(observed.to_numpy(dtype=float)).all():
        raise ValueError("integrated-transmission variables must be finite")
    if not observed[bitcoin_use].between(0.0, 1.0).all():
        raise ValueError("Bitcoin monetary-use share must lie in [0, 1]")
    frame["shock_x_sdr"] = frame[shock] * frame[sdr_exposure]
    frame["shock_x_btc_x_sdr"] = (
        frame[shock] * frame[bitcoin_use] * frame[sdr_exposure]
    )
    return frame


def estimate_integrated_transmission(
    data: pd.DataFrame,
    *,
    outcome: str,
    controls: Sequence[str] = (),
    shock: str = "policy_shock",
    bitcoin_use: str = "btc_use_share",
    sdr_exposure: str = "sdr_exposure",
    country: str = "country",
    period: str = "period",
    authority: str = "monetary_policy_authority",
) -> IntegratedTransmissionResult:
    """Estimate the integrated interaction specification with two-way FE.

    Includes shock, Bitcoin use, SDR exposure, shock×Bitcoin use,
    shock×SDR exposure, and shock×Bitcoin use×SDR exposure. The existing
    estimator constructs shock×Bitcoin use; the other interaction terms are
    passed as additional regressors. Cluster by monetary authority by default.
    """
    frame = prepare_integrated_panel(
        data, shock=shock, bitcoin_use=bitcoin_use, sdr_exposure=sdr_exposure
    )
    required = [outcome, shock, bitcoin_use, sdr_exposure, country, period, authority]
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise ValueError(f"missing integrated model columns: {missing}")
    regressors = [sdr_exposure, "shock_x_sdr", "shock_x_btc_x_sdr", *controls]
    estimate = estimate_transmission_panel(
        frame,
        outcome=outcome,
        shock=shock,
        adoption=bitcoin_use,
        controls=regressors,
        country=country,
        period=period,
        cluster_by=authority,
    )
    return IntegratedTransmissionResult(
        estimate=estimate,
        specification=(
            "outcome ~ shock + btc_use_share + shock×btc_use_share + "
            "sdr_exposure + shock×sdr_exposure + "
            "shock×btc_use_share×sdr_exposure + controls + country FE + period FE"
        ),
        interaction_terms=(
            "shock_x_adoption",
            "shock_x_sdr",
            "shock_x_btc_x_sdr",
        ),
        cluster_variable=authority,
    )
