# SDR exposure module (v0.6)

## Purpose and source-paper correspondence

This module operationalises selected observables corresponding to *How the SDR
Prevents Optimal Monetary Policy in a Nation*. The paper's central-bank loss
function adds a penalty for deviations from an SDR-consistent exchange rate;
it also discusses SDR allocations, sterilisation costs, policy coordination
externalities, and welfare loss.

The paper does not provide a downloadable country-period dataset, a complete
operational construction for the SDR-consistent exchange-rate benchmark, or
empirical coefficient estimates. Consequently, this software adds validation
and transparent transformations only. It does not establish the paper's
substantive claims or estimate a causal effect of SDR participation.

## Data contract

The empty `data/sdr_exposure_template.csv` is a schema, not an empirical
dataset. One row represents one country-period. Required fields are:

| Field | Meaning | Unit / constraint |
|---|---|---|
| `iso3` | ISO alpha-3 country identifier | Three uppercase letters |
| `period` | Country-period label | Nonblank; use one documented convention |
| `sdr_cumulative_allocations_usd` | Cumulative SDR allocations | USD; nonnegative |
| `sdr_holdings_usd` | SDR holdings | USD; nonnegative |
| `fx_reserves_usd` | Foreign-exchange reserves | USD; strictly positive |
| `gdp_usd` | Nominal GDP | USD; strictly positive |

Optional fields support additional measures:

- `exchange_rate_lcu_per_usd`: actual exchange rate, local currency per USD.
- `sdr_consistent_exchange_rate_lcu_per_usd`: benchmark in the identical
  quotation convention and units. The construction must be documented by the
  researcher; this package does not calculate the benchmark from basket
  weights.
- `sdr_allocation_lcu`: period allocation converted to local currency, not
  cumulative allocations.
- `policy_rate_pct` and `reserve_remuneration_rate_pct`: annual rates in
  percentage points, not decimal fractions.
- `source_id`, `source_vintage`, and `notes`: provenance metadata.

Do not mix USD and local-currency amounts, stock and flow measures, or
percentage rates and decimal rates. Record source, retrieval date, vintage,
definition, frequency, revisions, and licensing in the source registry.

## Constructed measures

`bsmpm.sdr.validate_sdr_panel` validates keys, required stock fields,
nonnegative stocks, positive GDP/reserve denominators, and finite optional
numeric values.

`bsmpm.sdr.construct_sdr_exposure_metrics` returns the input rows with:

```
sdr_allocation_to_gdp
    = sdr_cumulative_allocations_usd / gdp_usd

sdr_holdings_to_fx_reserves
    = sdr_holdings_usd / fx_reserves_usd

sdr_holdings_minus_cumulative_allocations_usd
    = sdr_holdings_usd - sdr_cumulative_allocations_usd

sdr_fx_deviation_log
    = log(actual_exchange_rate / sdr_consistent_exchange_rate)

sdr_sterilization_cost_lcu
    = (policy_rate_pct - reserve_remuneration_rate_pct)
      / 100 * sdr_allocation_lcu
```

The holdings-minus-cumulative-allocations measure is a descriptive stock
comparison. It is not represented as a complete IMF net-position accounting
measure. The FX deviation is available only when both exchange-rate series
are present and positive, in matching quotation conventions. Sterilisation
cost follows the paper's rate-differential-times-allocation expression; it is
an annualised reduced-form proxy and requires a period allocation in local
currency and annual rates. Missing optional inputs remain missing; the module
does not impute them.

## Relationship to the BSMPM estimator

The constructed SDR measures can be joined to the existing country-period
panel using `iso3` and the researcher's documented period key. A candidate
extended specification is:

```
outcome ~ policy_shock
        + btc_use_share
        + sdr_exposure
        + policy_shock:btc_use_share
        + policy_shock:sdr_exposure
        + policy_shock:btc_use_share:sdr_exposure
        + controls + country FE + time FE
```

This is a specification proposal, not a fitted model. The current estimator
does not automatically estimate this three-way interaction. Before doing so,
researchers must establish that Bitcoin monetary use and SDR exposure are
measured comparably, determine the correct timing and level of treatment
assignment, and defend the identifying assumptions. Cluster inference must
respect monetary-authority shock assignment; the number of clusters and
cross-sectional dependence remain material limitations.

## Example

```python
import pandas as pd
from bsmpm.sdr import construct_sdr_exposure_metrics

sdr_raw = pd.read_csv("data/sdr_exposure.csv")
sdr = construct_sdr_exposure_metrics(sdr_raw)
```

No source observations are supplied in this repository. The template remains
empty by design. Unit tests use synthetic fixtures solely to verify software
behaviour.
