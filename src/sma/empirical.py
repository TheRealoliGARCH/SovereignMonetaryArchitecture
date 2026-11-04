"""Country-panel estimation for the SMA monetary-transmission hypothesis.

The estimator is descriptive unless the policy-shock variable is externally
identified and the remaining identifying assumptions are defensible.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class PanelEstimate:
    coefficients: pd.DataFrame
    nobs: int
    clusters: int
    r_squared: float
    dropped_rows: int
    residual_degrees_of_freedom: int


def validate_panel(
    data: pd.DataFrame,
    *,
    outcome: str,
    shock: str,
    adoption: str,
    country: str = "country",
    period: str = "period",
    controls: Sequence[str] = (),
    extra_columns: Sequence[str] = (),
) -> tuple[pd.DataFrame, int]:
    """Validate a country-period panel and drop rows missing model variables.

    The country-period key must be unique. Adoption is a monetary-use share
    bounded by [0, 1], not an asset-ownership share.
    """
    required = list(dict.fromkeys([country, period, outcome, shock, adoption, *controls, *extra_columns]))
    missing = [name for name in required if name not in data.columns]
    if missing:
        raise ValueError(f"missing required columns: {missing}")
    frame = data.loc[:, required].copy()
    if frame[country].isna().any() or frame[period].isna().any():
        raise ValueError("country and period identifiers cannot be missing")
    if frame.duplicated([country, period]).any():
        raise ValueError("country-period observations must be unique")
    numeric = [outcome, shock, adoption, *controls]
    for name in numeric:
        frame[name] = pd.to_numeric(frame[name], errors="coerce")
    before = len(frame)
    frame = frame.dropna(subset=numeric).copy()
    if frame.empty:
        raise ValueError("no complete observations remain")
    if not np.isfinite(frame[numeric].to_numpy(dtype=float)).all():
        raise ValueError("numeric model variables must be finite")
    if not frame[adoption].between(0.0, 1.0).all():
        raise ValueError("adoption share must lie in [0, 1]")
    if frame[country].nunique() < 2:
        raise ValueError("at least two country clusters are required")
    if frame[period].nunique() < 2:
        raise ValueError("at least two time periods are required")
    return frame.reset_index(drop=True), before - len(frame)


def estimate_transmission_panel(
    data: pd.DataFrame,
    *,
    outcome: str,
    shock: str,
    adoption: str,
    controls: Sequence[str] = (),
    country: str = "country",
    period: str = "period",
    cluster_by: str | None = None,
) -> PanelEstimate:
    """Estimate a two-way fixed-effects interaction model.

    y_it = beta_0 shock_it + beta_1 adoption_it
           + beta_2 shock_it*adoption_it + controls + country FE + time FE + e_it.

    Standard errors cluster on ``cluster_by`` (country by default). For
    samples where multiple country markets share a monetary-policy authority,
    pass the authority identifier. The reported p-values use a standard-normal
    reference distribution and are asymptotic approximations.
    """
    cluster_column = cluster_by or country
    frame, dropped = validate_panel(
        data, outcome=outcome, shock=shock, adoption=adoption,
        country=country, period=period, controls=controls,
        extra_columns=(() if cluster_column in {country, period, outcome, shock, adoption, *controls} else (cluster_column,)),
    )
    if frame[cluster_column].isna().any():
        raise ValueError("cluster identifiers cannot be missing")
    frame["shock_x_adoption"] = frame[shock] * frame[adoption]
    regressors = [shock, adoption, "shock_x_adoption", *controls]
    x = frame[regressors].astype(float).copy()
    country_dummies = pd.get_dummies(frame[country].astype(str), prefix="country", drop_first=True, dtype=float)
    period_dummies = pd.get_dummies(frame[period].astype(str), prefix="period", drop_first=True, dtype=float)
    x = pd.concat([x.reset_index(drop=True), country_dummies, period_dummies], axis=1)
    x.insert(0, "const", 1.0)
    y = frame[outcome].to_numpy(dtype=float)
    design = x.to_numpy(dtype=float)
    nobs, nparams = design.shape
    rank = int(np.linalg.matrix_rank(design))
    if rank != nparams:
        raise ValueError("design matrix is rank deficient; check collinearity and panel variation")
    if nobs <= nparams:
        raise ValueError("insufficient residual degrees of freedom")
    # QR avoids forming X'X, which squares the design matrix condition number.
    q_matrix, r_matrix = np.linalg.qr(design, mode="reduced")
    diagonal = np.abs(np.diag(r_matrix))
    rank_tolerance = np.finfo(float).eps * max(design.shape) * diagonal.max()
    if np.count_nonzero(diagonal > rank_tolerance) != nparams:
        raise ValueError("design matrix is numerically rank deficient; check collinearity and panel variation")
    beta = np.linalg.solve(r_matrix, q_matrix.T @ y)
    residual = y - design @ beta
    groups = frame[cluster_column].to_numpy()
    codes, unique_groups = pd.factorize(groups, sort=False)
    g = len(unique_groups)
    if g < 2:
        raise ValueError("at least two clusters are required")
    # In QR coordinates, X_g' u_g = R' (Q_g' u_g). This computes the
    # one-way cluster sandwich without explicitly inverting X'X.
    meat_q = np.zeros((nparams, nparams), dtype=float)
    for code in range(g):
        mask = codes == code
        score = q_matrix[mask].T @ residual[mask]
        meat_q += np.outer(score, score)
    r_inverse = np.linalg.solve(r_matrix, np.eye(nparams))
    correction = (g / (g - 1.0)) * ((nobs - 1.0) / (nobs - nparams))
    covariance = correction * (r_inverse @ meat_q @ r_inverse.T)
    standard_errors = np.sqrt(np.maximum(np.diag(covariance), 0.0))
    t_stats = np.divide(beta, standard_errors, out=np.full_like(beta, np.nan), where=standard_errors > 0)
    p_values = np.array([math.erfc(abs(v) / math.sqrt(2.0)) if math.isfinite(v) else math.nan for v in t_stats])
    critical = 1.959963984540054
    result = pd.DataFrame({
        "term": x.columns,
        "coefficient": beta,
        "clustered_se": standard_errors,
        "z_statistic": t_stats,
        "p_value_normal_approx": p_values,
        "ci95_lower_normal": beta - critical * standard_errors,
        "ci95_upper_normal": beta + critical * standard_errors,
    })
    total = float(np.sum((y - y.mean()) ** 2))
    r_squared = 1.0 - float(residual @ residual) / total if total > 0 else math.nan
    return PanelEstimate(
        coefficients=result, nobs=nobs, clusters=g, r_squared=r_squared,
        dropped_rows=dropped, residual_degrees_of_freedom=nobs - nparams,
    )
