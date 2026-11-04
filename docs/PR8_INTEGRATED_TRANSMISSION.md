# PR #8 — Integrated monetary-policy transmission

## Purpose

This PR adds an integration layer over the existing BSMPM panel estimator,
authority-aware clustering, and SDR measurement module. It does not replace
those modules or retrieve data.

## Specification

The estimator composes the following country-period regression:

```text
outcome ~ policy_shock
        + btc_use_share
        + policy_shock × btc_use_share
        + sdr_exposure
        + policy_shock × sdr_exposure
        + policy_shock × btc_use_share × sdr_exposure
        + controls + country FE + period FE
```

The interaction variables are constructed in `bsmpm.integrated`. The default
cluster variable is the monetary-policy authority. Researchers may choose an
alternative documented SDR exposure measure before estimation.

## Data contract

- `btc_use_share` is a monetary-use share in [0, 1], not an ownership share.
- `sdr_exposure` is a numeric, source-documented country-period measure.
- Policy shocks and outcome variables must share a defensible time alignment.
- The authority identifier must represent the institution responsible for the
  policy shock; country labels are not a substitute where authorities are shared.

## Interpretation limits

This is a two-way fixed-effects conditional-association estimator. The triple
interaction does not establish causal moderation unless the shock is
identified and the remaining assumptions are defensible. The inherited
authority-clustered sandwich inference is asymptotic and can be unreliable with
few clusters. No empirical observations or estimates are supplied by this PR.

## Validation

Deterministic synthetic tests check interaction construction, authority
clustering, and invalid Bitcoin-use shares. Passing tests validates code paths,
not the economic hypothesis.
