# PR #12 — Structural monetary-dynamics scaffold

## Purpose

This PR adds a transparent one-period state-transition scaffold to organize
future structural work. It is not a solved general-equilibrium model, an
estimated model, or a calibrated welfare framework.

## State vector

The state is
```text
x_t = (inflation_gap, output_gap, exchange_rate_gap,
       bitcoin_use_share, sdr_exposure)
```

A policy shock is scaled by an assumed insulation function:
```text
effective_shock = policy_shock
                  × (1 - insulation_parameter × bitcoin_use_share)
```

The inflation, output, and exchange-rate gaps then evolve under explicitly
named persistence and loading parameters. SDR exposure enters the exchange-rate
scenario equation through a sensitivity parameter. Bitcoin-use share and SDR
exposure are held fixed over this one-period transition; endogenous evolution
is not yet specified.

## Loss function

The scenario loss is quadratic in inflation, output, and exchange-rate gaps,
with an optional SDR-exposure penalty. The weights are user-supplied scenario
parameters. This objective is not claimed to be a central bank's revealed
objective or a welfare measure.

## Research requirements before structural interpretation

A structural model requires microfoundations or defensible behavioural
equations, equilibrium conditions, timing conventions, parameter restrictions,
identification or calibration strategy, solution method, and validation.
The current scaffold provides named state variables and transparent scenario
equations only. No parameter values are estimated from data, and the default
values are illustrative software defaults.
