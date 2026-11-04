# PR #11 — Sovereign monetary autonomy index

## Method

The module `sma.autonomy` constructs a transparent weighted composite from
researcher-supplied components normalized to [0,1]. Higher values must be
defined as either autonomy-enhancing (+1) or autonomy-reducing (-1) through an
explicit direction map.

Default component polarity:
- Domestic monetary control: positive.
- Exchange-rate flexibility: positive.
- Reserve adequacy: positive.
- SDR exposure: negative (higher exposure is treated as a constraint).

Bitcoin monetary-use share has no default polarity. Its effect on autonomy is
the empirical and theoretical question under study; researchers must specify
both its weight and direction explicitly before including it.

## Weighting and missingness

Weights must be nonnegative and sum to one. The index does not estimate weights,
normalize raw data, impute missing values, or renormalize weights around
missing components. All selected components must be complete and lie in [0,1].
This avoids concealing missingness or embedding sample-dependent scaling.

## Interpretation

The index is a researcher-defined composite, not an objective measurement of
sovereignty, a causal outcome, or a validated ranking of countries. Component
selection, normalization, direction, and weights require theoretical
justification and sensitivity analysis. Report components alongside the
composite; do not publish a single score without its construction metadata.
