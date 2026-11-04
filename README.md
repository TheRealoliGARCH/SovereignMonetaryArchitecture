# Bitcoin–Sovereign Monetary Policy Model (BSMPM)

A reproducible Python implementation of the BSMPM research architecture. The repository combines reduced-form analytical building blocks with an initial empirical country-panel estimator. It is **not yet a calibrated or estimated general-equilibrium model**.

## Scope

- Monetary transmission under fiat/Bitcoin transaction shares.
- Nonlinear transmission attenuation and critical adoption thresholds.
- Endogenous Bitcoin-adoption fixed points with logistic network effects.
- Reduced-form seigniorage sensitivity and Bitcoin-sector liquidity shortfall.
- Illustrative adoption-welfare trade-offs and scenario simulation.
- Country-period panel validation and two-way fixed-effects estimation.
- CSV data ingestion, source-registry validation, and SHA-256 provenance manifests.
- A source-audited 29-country monetary-policy sample frame and empirical series catalogue.
- Authority-level clustered inference and event-to-month/quarter shock aggregation.
- Separate event, daily-market, and lower-frequency macro data architecture.
- SDR exposure metrics, exchange-rate deviation measures, and sterilisation-cost proxies.

## Model conventions

1. The adoption share (s) is a *monetary-use/transaction share*, not the Bitcoin share of household wealth.
2. The linear transmission coefficient is a reduced-form weighted average; it does not establish that every Bitcoin transaction is insulated from domestic rates.
3. The nonlinear transmission function is an alternative parameterization and must be constrained to economically meaningful values.
4. The adoption fixed-point equation can have multiple fixed points for appropriate parameter values. Strong feedback alone does not guarantee three roots for every intercept.
5. Seigniorage sensitivity and welfare are illustrative reduced forms, not accounting identities or calibrated welfare estimates.
6. No empirical country dataset is bundled. Synthetic data are used only for deterministic software tests.

## Empirical estimator (v0.2)

The module `bsmpm.empirical` estimates a country-period specification with country and time fixed effects:

`outcome ~ policy_shock + adoption_share + policy_shock × adoption_share + controls + country FE + time FE`.

The interaction coefficient measures how the conditional response to the policy shock varies with Bitcoin monetary-use share. Standard errors are clustered by country. The module validates unique country-period keys, finite numeric data, and the [0,1] adoption-share domain.

**Causal interpretation is not automatic.** The policy shock must be plausibly exogenous, and reverse causality, time-varying confounding, measurement error, and cross-sectional dependence require separate treatment. The estimator reports normal-reference inference approximations and is intended as a transparent baseline. See [docs/EMPIRICAL.md](docs/EMPIRICAL.md) for the specification, data contract, and limitations.

## Empirical data ingestion (v0.3)

The module `bsmpm.data_io` validates country-period CSVs and source-registry
metadata, counts missing numeric observations, and creates a JSON provenance
manifest with SHA-256 file hashes. The repository includes empty schema
templates only; no observed country data are fabricated or bundled. See
`docs/DATA_INGESTION.md` and `data/README.md`.

The ingestion layer records source URLs but does not fetch them or validate
licensing, source authenticity, construct validity, or causal identification.

## Empirical source audit (v0.4)

The v0.4 source audit adds `data/country_roster.csv`, `data/source_catalog.csv`,
and an authority-aware event-shock template. The IMF WP/24/224 frame contains
29 country markets but 20 monetary authorities; ten euro-area markets share
the ECB shock series. Bitcoin exchange turnover and search interest are
explicitly labelled proxies, not monetary-use shares. No raw observations are
fabricated or included. See `docs/PR4_SOURCE_AUDIT.md`.

## Authority-aware inference and frequencies (v0.5)

The panel estimator accepts `cluster_by`; use
`cluster_by="monetary_policy_authority"` when multiple country markets share
one policy-shock authority. The new `bsmpm.frequency` module aggregates
event-level shocks to monthly or quarterly authority series and maps those
series to country panels through the audited roster. It does not interpolate
macro data to daily frequency. See `docs/PR5_AUTHORITY_MULTIFREQUENCY.md`.

## SDR exposure module (v0.6)

The `bsmpm.sdr` module validates country-period SDR allocations, holdings,
reserve stocks and GDP, and constructs explicitly defined exposure ratios.
Where source-documented optional inputs exist, it also constructs an
SDR-consistent exchange-rate deviation and a sterilisation-cost proxy. The
repository includes an empty data schema only; no SDR observations or
benchmark exchange rates are fabricated. See `docs/PR6_SDR_EXPOSURE.md`.

## Requirements

Python 3.10+; NumPy and pandas are required. Matplotlib is optional for simulation plots.

Install:

```bash
python -m pip install -e ".[dev]"
```

## Quick start

Run all tests:

```bash
python -m unittest discover -s tests -v
```

Run illustrative scenarios:

```bash
python -m bsmpm.simulate --output outputs
```

## Repository layout

- `src/bsmpm/model.py`: analytical reduced-form functions.
- `src/bsmpm/empirical.py`: panel validation and fixed-effects estimator.
- `src/bsmpm/data_io.py`: ingestion, source registry, and provenance manifest.
- `src/bsmpm/frequency.py`: authority-level event aggregation and panel alignment.
- `src/bsmpm/sdr.py`: SDR exposure validation and derived metrics.
- `src/bsmpm/source_audit.py`: country-frame validation and source-audit checks.
- `src/bsmpm/simulate.py`: illustrative scenario runner.
- `tests/`: deterministic unit tests, including a synthetic panel.
- `docs/MODEL.md`: v0.1 equations and assumptions.
- `docs/EMPIRICAL.md`: v0.2 estimator, data contract, and identification limitations.
- `docs/DATA_INGESTION.md`: v0.3 ingestion contract and provenance workflow.
- `docs/PR4_SOURCE_AUDIT.md`: v0.4 country frame, source catalogue, and measurement audit.
- `docs/PR5_AUTHORITY_MULTIFREQUENCY.md`: v0.5 inference and frequency architecture.
- `docs/PR6_SDR_EXPOSURE.md`: v0.6 SDR data contract, measures, and limitations.
- `.github/workflows/tests.yml`: Python 3.10–3.12 CI.

## Research roadmap

1. Acquire and license-clear the event-level shock series and outcome data identified in the v0.4 source audit.
2. Separate Bitcoin ownership, payment/transaction use, settlement use, and contract denomination.
3. Validate policy-shock construction and investigate defensible identification strategies.
4. Add robustness checks for heterogeneous effects, serial/cross-sectional dependence, and missingness.
5. Extend toward household, firm, bank, and central-bank optimization and a coherent equilibrium model.
6. Publish data provenance, estimation code, calibration files, and reproducibility metadata.

## Interpretation

Unit tests verify software behaviour, not economic assumptions or causal claims. Empirical conclusions require defensible measurements, identified shocks, robustness analysis, and transparent reporting.
