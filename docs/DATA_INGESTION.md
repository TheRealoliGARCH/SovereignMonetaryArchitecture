# Empirical data ingestion and provenance (v0.3)

## Purpose

The v0.3 ingestion layer creates a reproducible boundary between source data and
the v0.2 panel estimator. It validates supplied country-period CSVs and records
file identity and source metadata. It does not fetch external series, adjudicate
source quality, estimate missing observations, or establish causal identification.

## Panel contract

One row represents one country-period observation. Required columns:

| Column | Meaning | Constraint |
| --- | --- | --- |
| country | Stable country identifier | Nonblank |
| period | Common time-period identifier | Nonblank |
| outcome | Defined monetary-transmission outcome | Numeric or missing |
| policy_shock | Documented monetary-policy shock | Numeric or missing |
| btc_use_share | Measured Bitcoin monetary-use share | Numeric or missing; observed values in [0,1] |

The country-period key must be unique. Nonblank nonnumeric values and infinite
values are rejected. Missing numeric cells are retained and counted; the v0.2
estimator subsequently performs complete-case deletion over its selected model
variables. This separation makes missingness visible before estimation.

## Measurement discipline

Do not conflate Bitcoin asset ownership or portfolio allocation, payment or
transaction use, settlement use, and denomination of prices, wages, debts, or
contracts. A variable named btc_use_share must have an operational definition
that matches the intended monetary-use construct. Retain distinct constructs
as separate series.

## Source registry

The registry template requires a unique source_id-variable pair and records
provider, URL, definition, unit, frequency, coverage, ISO retrieval date,
license, transformation, and status. URLs are metadata only: the validator does
not request them. Check terms of use and redistribution rights before storing
or publishing observations.

## API

- validate_empirical_dataset(data): validates a DataFrame and returns row,
  country, period, and missing-value counts.
- load_country_panel(path): loads UTF-8 CSV and validates its structure.
- validate_source_registry(registry): validates source metadata.
- build_provenance_manifest(...): returns hashes and validation summaries.
- write_provenance_manifest(...): writes JSON.

Example:

    from bsmpm.data_io import write_provenance_manifest

    write_provenance_manifest(
        "data/raw/country_panel.csv",
        source_registry_path="data/metadata/source_registry.csv",
        output_path="data/metadata/provenance_manifest.json",
        metadata={"study_version": "0.3"},
    )

## Interpretation and limitations

A SHA-256 digest makes subsequent file-integrity checks possible; it does not
authenticate the publisher or validate the underlying economic construct.
Structural validation cannot resolve measurement error, non-random missingness,
cross-country comparability, policy-shock endogeneity, reverse causality, or
cross-sectional dependence. The pipeline deliberately does not create a
purported empirical dataset from illustrative values.

## Reproducibility checklist

1. Archive original source extracts where permitted.
2. Complete one registry row per source-variable series.
3. Preserve original units and document transformations.
4. Record retrieval dates and revision/vintage information in metadata.
5. Validate the panel and source registry.
6. Generate and retain a provenance manifest.
7. Run the estimator on the explicitly selected sample and report exclusions.
