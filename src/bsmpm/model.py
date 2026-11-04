"""Core reduced-form equations for BSMPM.

These functions implement the explicitly stated equations. They do not claim
that the reduced forms are universally valid or empirically estimated.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable


def _finite(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def _share(name: str, value: float) -> float:
    value = _finite(name, value)
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must lie in [0, 1]")
    return value


def logistic(z: float) -> float:
    """Numerically stable logistic map."""
    z = _finite("z", z)
    if z >= 0:
        e = math.exp(-z)
        value = 1.0 / (1.0 + e)
    else:
        e = math.exp(z)
        value = e / (1.0 + e)
    # Preserve an interior floating-point value when mathematically < 1.
    return min(math.nextafter(1.0, 0.0), max(math.nextafter(0.0, 1.0), value))


def monetary_transmission_linear(
    adoption_share: float, kappa_fiat: float, kappa_bitcoin: float
) -> float:
    """K(s)=(1-s)kappa_fiat+s*kappa_bitcoin.

    Adoption is the share of relevant domestic economic activity denominated
    or transacted in Bitcoin, not an asset-ownership share.
    """
    s = _share("adoption_share", adoption_share)
    kf = _finite("kappa_fiat", kappa_fiat)
    kb = _finite("kappa_bitcoin", kappa_bitcoin)
    if kf < kb:
        raise ValueError("kappa_fiat must be >= kappa_bitcoin for attenuation")
    if kb < 0:
        raise ValueError("transmission coefficients must be nonnegative")
    return (1.0 - s) * kf + s * kb


def monetary_transmission_nonlinear(
    adoption_share: float, kappa_fiat: float, alpha: float, beta: float
) -> float:
    """Illustrative K(s)=kappa_fiat-alpha*s-beta*s**2.

    The returned value may be negative for inadmissible parameter choices;
    callers should impose K(s)>=0 or use constrained calibration.
    """
    s = _share("adoption_share", adoption_share)
    kf = _finite("kappa_fiat", kappa_fiat)
    a = _finite("alpha", alpha)
    b = _finite("beta", beta)
    if kf < 0 or a < 0 or b < 0:
        raise ValueError("kappa_fiat, alpha and beta must be nonnegative")
    return kf - a * s - b * s * s


def critical_adoption_linear(
    kappa_fiat: float, kappa_bitcoin: float, minimum_capacity: float
) -> float:
    """Maximum s satisfying K(s)>=minimum_capacity; returns None if infeasible.

    The endpoint s=0 must satisfy the requirement. If even s=1 satisfies it,
    the returned threshold is 1. Otherwise the threshold is in [0,1].
    """
    kf = _finite("kappa_fiat", kappa_fiat)
    kb = _finite("kappa_bitcoin", kappa_bitcoin)
    km = _finite("minimum_capacity", minimum_capacity)
    if kf < kb or kb < 0:
        raise ValueError("require kappa_fiat >= kappa_bitcoin >= 0")
    if km < 0:
        raise ValueError("minimum_capacity must be nonnegative")
    if kf < km:
        raise ValueError("minimum transmission requirement is infeasible at s=0")
    if kb >= km or kf == kb:
        return 1.0
    return (kf - km) / (kf - kb)


def critical_adoption_quadratic(
    kappa_fiat: float, alpha: float, beta: float, minimum_capacity: float
) -> float:
    """Largest admissible s in [0,1] satisfying kf-alpha*s-beta*s² >= Kmin."""
    kf = _finite("kappa_fiat", kappa_fiat)
    a = _finite("alpha", alpha)
    b = _finite("beta", beta)
    km = _finite("minimum_capacity", minimum_capacity)
    if min(kf, a, b, km) < 0:
        raise ValueError("parameters and minimum_capacity must be nonnegative")
    if kf < km:
        raise ValueError("minimum transmission requirement is infeasible at s=0")
    if kf - a - b >= km:
        return 1.0
    if a == 0 and b == 0:
        return 1.0
    if b == 0:
        return min(1.0, (kf - km) / a)
    disc = a * a + 4.0 * b * (kf - km)
    root = (-a + math.sqrt(disc)) / (2.0 * b)
    return max(0.0, min(1.0, root))


def adoption_fixed_points(
    intercept: float, feedback: float, grid_size: int = 20_001, tolerance: float = 1e-8
) -> list["AdoptionFixedPoint"]:
    """Find roots of s=logistic(intercept+feedback*s) on [0,1].

    A dense-grid sign scan plus bisection is used. The method is deterministic
    and suitable for model exploration, not a formal proof of root count.
    """
    z = _finite("intercept", intercept)
    feedback = _finite("feedback", feedback)
    if grid_size < 101:
        raise ValueError("grid_size must be at least 101")
    if tolerance <= 0 or not math.isfinite(tolerance):
        raise ValueError("tolerance must be positive and finite")

    def f(s: float) -> float:
        return logistic(z + feedback * s) - s

    xs = [i / (grid_size - 1) for i in range(grid_size)]
    roots: list[float] = []
    for left, right in zip(xs[:-1], xs[1:]):
        fl, fr = f(left), f(right)
        if abs(fl) <= tolerance:
            roots.append(left)
        if fl * fr < 0:
            lo, hi = left, right
            for _ in range(80):
                mid = (lo + hi) / 2.0
                fm = f(mid)
                if abs(fm) <= tolerance or hi - lo <= tolerance:
                    lo = hi = mid
                    break
                if f(lo) * fm <= 0:
                    hi = mid
                else:
                    lo = mid
            roots.append((lo + hi) / 2.0)
    if abs(f(1.0)) <= tolerance:
        roots.append(1.0)

    unique: list[float] = []
    for root in sorted(roots):
        if not unique or abs(root - unique[-1]) > 10 * tolerance:
            unique.append(root)

    results = []
    for root in unique:
        slope = feedback * root * (1.0 - root)
        results.append(
            AdoptionFixedPoint(
                share=root,
                mapping_slope=slope,
                locally_stable_under_naive_iteration=abs(slope) < 1.0,
            )
        )
    return results


@dataclass(frozen=True)
class AdoptionFixedPoint:
    share: float
    mapping_slope: float
    locally_stable_under_naive_iteration: bool


def seigniorage_proxy(
    baseline_real_seigniorage: float, adoption_share: float, sensitivity: float
) -> float:
    """Reduced-form S(s)=S0*(1-eta*s), not a money-demand identity."""
    s = _share("adoption_share", adoption_share)
    s0 = _finite("baseline_real_seigniorage", baseline_real_seigniorage)
    eta = _finite("sensitivity", sensitivity)
    if s0 < 0 or not 0 <= eta <= 1:
        raise ValueError("baseline seigniorage must be >=0 and sensitivity in [0,1]")
    return s0 * (1.0 - eta * s)


def liquidity_shortfall(
    stressed_btc_liability: float,
    available_btc_liquidity: float,
    enforceable_btc_funding: float,
) -> float:
    """Uncovered BTC liquidity need, in BTC units."""
    values = [
        _finite("stressed_btc_liability", stressed_btc_liability),
        _finite("available_btc_liquidity", available_btc_liquidity),
        _finite("enforceable_btc_funding", enforceable_btc_funding),
    ]
    if any(v < 0 for v in values):
        raise ValueError("liquidity amounts must be nonnegative")
    liabilities, liquidity, funding = values
    return max(0.0, liabilities - liquidity - funding)


def welfare(
    adoption_share: float,
    benefit_linear: float,
    benefit_curvature: float,
    cost_linear: float,
    cost_curvature: float,
) -> float:
    """Illustrative W(s)=b1*s-b2*s²/2-c1*s-c2*s²/2."""
    s = _share("adoption_share", adoption_share)
    b1 = _finite("benefit_linear", benefit_linear)
    b2 = _finite("benefit_curvature", benefit_curvature)
    c1 = _finite("cost_linear", cost_linear)
    c2 = _finite("cost_curvature", cost_curvature)
    return (b1 - c1) * s - 0.5 * (b2 + c2) * s * s


def welfare_optimum(
    benefit_linear: float, benefit_curvature: float, cost_linear: float, cost_curvature: float
) -> float:
    """Constrained maximizer of the quadratic welfare function on [0,1]."""
    b1 = _finite("benefit_linear", benefit_linear)
    b2 = _finite("benefit_curvature", benefit_curvature)
    c1 = _finite("cost_linear", cost_linear)
    c2 = _finite("cost_curvature", cost_curvature)
    curvature = b2 + c2
    if curvature <= 0:
        return 1.0 if b1 > c1 else 0.0
    return min(1.0, max(0.0, (b1 - c1) / curvature))
