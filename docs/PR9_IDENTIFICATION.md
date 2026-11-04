# PR #9 — Identification and robustness diagnostics

This PR adds a pre-estimation diagnostic report for the integrated panel design.

## Diagnostics

- Counts complete observations, countries, periods, and monetary-policy authorities.
- Measures within-authority and between-authority policy-shock dispersion.
- Counts authorities with within-authority shock variation.
- Measures within-country variation in Bitcoin monetary-use share.
- Reports complete-case coverage and warns when the number of authority clusters
  is below a configurable threshold (30 by default).

## What this does not do

The diagnostics do not prove shock exogeneity, validate an instrument, establish
parallel trends, correct measurement error, or solve cross-sectional dependence.
No instrumental-variable estimate, event-study causal estimate, wild-cluster
bootstrap, or placebo test is claimed. Those require a specified research
design and appropriate data. The report is intended to reveal design support
and obvious variation/cluster limitations before estimation.
