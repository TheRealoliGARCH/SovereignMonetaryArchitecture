"""Identification and design diagnostics; no causal estimator is implied."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Sequence

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class IdentificationDiagnostics:
    observations: int
    countries: int
    periods: int
    authorities: int
    authorities_with_within_variation: int
    shock_within_authority_sd: float
    shock_between_authority_sd: float
    adoption_within_country_sd: float
    complete_case_share: float
    warnings: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def diagnose_identification(
    data: pd.DataFrame,
    *,
    shock: str = "policy_shock",
    adoption: str = "btc_use_share",
    country: str = "country",
    period: str = "period",
    authority: str = "monetary_policy_authority",
    required_controls: Sequence[str] = (),
    few_cluster_threshold: int = 30,
) -> IdentificationDiagnostics:
    """Summarise variation and panel support relevant to identification.

    This is a pre-estimation diagnostic, not a test of shock exogeneity,
    instrument validity, parallel trends, or causal identification.
    """
    required = [shock, adoption, country, period, authority, *required_controls]
    missing = [c for c in required if c not in data.columns]
    if missing:
        raise ValueError(f"missing diagnostic columns: {missing}")
    frame = data.loc[:, required].copy()
    n_input = len(frame)
    frame[shock] = pd.to_numeric(frame[shock], errors="coerce")
    frame[adoption] = pd.to_numeric(frame[adoption], errors="coerce")
    complete = frame.dropna(subset=required).copy()
    if complete.empty:
        raise ValueError("no complete observations available for diagnostics")
    numeric = complete[[shock, adoption, *required_controls]].to_numpy(dtype=float)
    if not np.isfinite(numeric).all():
        raise ValueError("diagnostic numeric variables must be finite")
    if not complete[adoption].between(0, 1).all():
        raise ValueError("Bitcoin monetary-use share must lie in [0, 1]")
    if complete.duplicated([country, period]).any():
        raise ValueError("country-period observations must be unique")

    auth_means = complete.groupby(authority, observed=True)[shock].mean()
    within = complete[shock] - complete.groupby(authority, observed=True)[shock].transform("mean")
    within_sd = float(within.std(ddof=1)) if len(within) > 1 else 0.0
    between_sd = float(auth_means.std(ddof=1)) if len(auth_means) > 1 else 0.0
    within_var = complete.groupby(authority, observed=True)[shock].nunique()
    variable_authorities = int((within_var > 1).sum())
    adoption_within = complete[adoption] - complete.groupby(country, observed=True)[adoption].transform("mean")
    adoption_sd = float(adoption_within.std(ddof=1)) if len(adoption_within) > 1 else 0.0

    authorities = int(complete[authority].nunique())
    countries = int(complete[country].nunique())
    periods = int(complete[period].nunique())
    warnings = []
    if authorities < few_cluster_threshold:
        warnings.append(
            f"Only {authorities} authority clusters: conventional cluster-robust "
            "normal-reference inference may be unreliable."
        )
    if variable_authorities < 2:
        warnings.append("Fewer than two authorities exhibit within-authority shock variation.")
    if within_sd <= 1e-12:
        warnings.append("Policy shock has effectively no within-authority variation.")
    if adoption_sd <= 1e-12:
        warnings.append("Bitcoin-use share has effectively no within-country variation.")
    if countries < 2 or periods < 2:
        warnings.append("Insufficient cross-sectional or time support for two-way fixed effects.")
    if len(complete) < n_input:
        warnings.append("Complete-case diagnostics exclude rows with missing model variables.")
    return IdentificationDiagnostics(
        observations=len(complete), countries=countries, periods=periods,
        authorities=authorities, authorities_with_within_variation=variable_authorities,
        shock_within_authority_sd=within_sd, shock_between_authority_sd=between_sd,
        adoption_within_country_sd=adoption_sd,
        complete_case_share=len(complete) / n_input if n_input else 0.0,
        warnings=tuple(warnings),
    )
