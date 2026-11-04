# Empirical data directory

## Current contents

- `panel_template.csv`: v0.3 minimal country-period estimator schema.
- `source_registry_template.csv`: source metadata contract.
- `country_roster.csv`: 29-country market frame from IMF WP/24/224, including
  shared monetary-policy authority and shock-series identifiers. The 2000-2022
  fields describe the paper's overall study window, not guaranteed coverage in
  every country; country-specific event coverage varies and China's series
  begins in 2008.
- `source_catalog.csv`: source-audited catalogue of candidate monetary,
  macroeconomic, crypto-activity and survey series.
- `shock_events_template.csv`: authority-aware event-level shock schema.

The roster and catalogue are metadata, not observation-level empirical data.
No country-period outcomes, policy-shock realizations or Bitcoin monetary-use
shares have been fabricated or bundled.

## Measurement discipline

Bitcoin ownership, portfolio holdings, exchange turnover, search interest,
all-crypto activity, payments, remittances, settlement and contract
denomination are distinct constructs. None is silently substituted for
`btc_use_share`.

## Provenance

The catalogue records source URLs, definitions, units, frequency, coverage,
audit retrieval date, licensing/access caveats and admissible transformations.
The retrieval date is the date the source metadata were reviewed; it is not the
date on which observations were downloaded. Check provider terms before
redistributing any observations.

See `docs/PR4_SOURCE_AUDIT.md` for sample construction, IMF shock methodology,
euro-area shared-shock treatment, Bitcoin proxy limitations and the next data
acquisition gate.


## Authority-level event aggregation (v0.5)

Use `shock_events_template.csv` for announcement-level records. Aggregate
event shocks by monetary authority, shock-series ID, and calendar month or
quarter before attaching them to country-period outcome panels. The same
authority-period innovation may map to several country markets; those market
rows must not be interpreted as independent shock realizations. See
`docs/PR5_AUTHORITY_MULTIFREQUENCY.md`.


## SDR exposure data (v0.6)

`sdr_exposure_template.csv` defines an empty country-period schema for
cumulative allocations, holdings, foreign-exchange reserves, GDP, optional
exchange-rate benchmarks and sterilisation inputs. It is not an observations
file. Keep cumulative allocation stocks separate from period allocation
flows; retain currency units, rate conventions, source vintages and licensing.
See `docs/PR6_SDR_EXPOSURE.md`.
