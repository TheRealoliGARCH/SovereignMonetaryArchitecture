"""Transparent structural-dynamics scaffold for sovereign monetary systems.

Equations here are explicit scenario assumptions, not estimated structural
relationships or a solved general-equilibrium model.
"""
from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class MonetaryState:
    inflation_gap: float
    output_gap: float
    exchange_rate_gap: float
    bitcoin_use_share: float
    sdr_exposure: float


@dataclass(frozen=True)
class StructuralParameters:
    inflation_persistence: float = 0.7
    output_persistence: float = 0.6
    exchange_rate_persistence: float = 0.5
    policy_to_inflation: float = 0.2
    policy_to_output: float = -0.3
    exchange_to_inflation: float = 0.1
    sdr_shock_sensitivity: float = 0.1
    bitcoin_transmission_insulation: float = 0.0
    inflation_weight: float = 1.0
    output_weight: float = 1.0
    exchange_rate_weight: float = 0.0
    sdr_penalty_weight: float = 0.0


@dataclass(frozen=True)
class StructuralTransition:
    state: MonetaryState
    effective_policy_shock: float
    policy_loss: float


def _finite(name: str, value: float) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def validate_state(state: MonetaryState) -> None:
    for name in (
        "inflation_gap", "output_gap", "exchange_rate_gap",
        "bitcoin_use_share", "sdr_exposure",
    ):
        _finite(name, getattr(state, name))
    if not 0.0 <= state.bitcoin_use_share <= 1.0:
        raise ValueError("bitcoin_use_share must lie in [0, 1]")
    if state.sdr_exposure < 0:
        raise ValueError("sdr_exposure must be nonnegative")


def validate_parameters(parameters: StructuralParameters) -> None:
    for name, value in parameters.__dict__.items():
        _finite(name, value)
    for name in ("inflation_weight", "output_weight", "exchange_rate_weight", "sdr_penalty_weight"):
        if getattr(parameters, name) < 0:
            raise ValueError(f"{name} must be nonnegative")
    if not 0.0 <= parameters.bitcoin_transmission_insulation <= 1.0:
        raise ValueError("bitcoin_transmission_insulation must lie in [0, 1]")


def policy_loss(state: MonetaryState, parameters: StructuralParameters) -> float:
    """Quadratic scenario loss, not a welfare estimate."""
    validate_state(state)
    validate_parameters(parameters)
    return (
        parameters.inflation_weight * state.inflation_gap ** 2
        + parameters.output_weight * state.output_gap ** 2
        + parameters.exchange_rate_weight * state.exchange_rate_gap ** 2
        + parameters.sdr_penalty_weight * state.sdr_exposure ** 2
    ) / 2.0


def transition_one_period(
    state: MonetaryState,
    policy_shock: float,
    parameters: StructuralParameters = StructuralParameters(),
) -> StructuralTransition:
    """Advance one period under an explicitly parameterized linear scenario.

    Effective shock is scaled by (1 - insulation * Bitcoin monetary-use share).
    This is a modelling assumption for sensitivity analysis, not an established
    property of Bitcoin transactions or monetary transmission.
    """
    validate_state(state)
    validate_parameters(parameters)
    shock = _finite("policy_shock", policy_shock)
    effective = shock * (
        1.0 - parameters.bitcoin_transmission_insulation * state.bitcoin_use_share
    )
    next_state = MonetaryState(
        inflation_gap=(
            parameters.inflation_persistence * state.inflation_gap
            - parameters.policy_to_inflation * effective
            + parameters.exchange_to_inflation * state.exchange_rate_gap
        ),
        output_gap=(
            parameters.output_persistence * state.output_gap
            + parameters.policy_to_output * effective
        ),
        exchange_rate_gap=(
            parameters.exchange_rate_persistence * state.exchange_rate_gap
            + parameters.sdr_shock_sensitivity * state.sdr_exposure * shock
        ),
        bitcoin_use_share=state.bitcoin_use_share,
        sdr_exposure=state.sdr_exposure,
    )
    return StructuralTransition(
        state=next_state,
        effective_policy_shock=effective,
        policy_loss=policy_loss(next_state, parameters),
    )
