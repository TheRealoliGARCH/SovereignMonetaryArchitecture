# Authority-aware inference and multi-frequency architecture (v0.5)

## Why the unit of inference changes

The v0.4 source frame contains 29 country markets but 20 monetary-policy
authorities. Ten euro-area country markets map to the ECB shock series. Where
the policy innovation is common to several country rows, those rows do not
represent independent policy-shock realizations. Country-clustered standard
errors alone do not reflect that assignment structure.

The panel estimator therefore accepts `cluster_by`. The default remains
country clustering for backward compatibility. For a panel whose policy
shocks are assigned at authority level, pass
`cluster_by="monetary_policy_authority"`. The reported cluster count is the
number of distinct nonmissing authority identifiers in the estimation sample.

This is a one-way authority-clustered sandwich covariance estimator with the
existing conventional finite-sample correction. It is not a two-way clustered
or wild-cluster-bootstrap estimator. Twenty authority clusters are still a
modest number; normal-reference p-values and confidence intervals remain
approximate. Inference should be supplemented by small-cluster methods and
sensitivity analysis before substantive claims.

## Event-to-panel pipeline

The new `sma.frequency.aggregate_event_shocks` function:
1. parses announcement timestamps as UTC;
2. assigns each event to a calendar month or quarter;
3. sums specified basis-point shock columns within authority, shock-series ID,
   and period; and
4. retains the number of events contributing to each aggregate.

Only `frequency="M"` and `frequency="Q"` are accepted. No-event periods are
not silently filled with zero. The default shock columns are
`epsilon_mp_bp` and `epsilon_cbi_bp`; callers may specify another documented
set of numeric shock columns.

`sma.frequency.attach_authority_shocks` maps an authority-period table to
country-period outcomes through the country roster. It enforces unique
country-period observations, one roster mapping per country, and unique
authority-series-period shock records. It rejects unmatched observations
rather than imputing shocks.

## Keep frequencies separate

The architecture distinguishes:
- **Event level:** announcement timestamp, raw and orthogonalized shocks,
  event identifiers, source vintage.
- **Daily market level:** market prices, yields, exchange rates, liquidity,
  volatility, and trading measures.
- **Monthly/quarterly macro level:** monetary outcomes, controls, and
  authority-aggregated shocks.

An event-to-month/quarter sum is a defined aggregation of event shocks, not a
license to interpolate monthly or quarterly macro variables to daily
frequency. Daily market responses should be studied with event windows or
daily local projections; lower-frequency macro outcomes require an explicitly
matched monthly or quarterly design. The two designs should not be pooled by
mechanical frequency conversion.

## Example

```python
from sma.frequency import aggregate_event_shocks, attach_authority_shocks
from sma.empirical import estimate_transmission_panel

authority_month = aggregate_event_shocks(events, frequency="M")
panel = attach_authority_shocks(country_outcomes, country_roster, authority_month)
result = estimate_transmission_panel(
    panel,
    outcome="outcome",
    shock="epsilon_mp_bp",
    adoption="btc_use_share",
    cluster_by="monetary_policy_authority",
)
```

The example presumes the outcome and Bitcoin monetary-use share are actually
measured at the monthly country level. The event aggregation does not supply
either variable.

## Interpretation limits

- Clustering by authority aligns the covariance grouping more closely with
  common policy-shock assignment; it does not create additional independent
  authorities or solve cross-sectional dependence beyond that grouping.
- The interaction remains a conditional association unless shock
  exogeneity and the remaining identification assumptions are defended.
- The number and composition of authority clusters must be reported.
- Event aggregation is only meaningful when shock units, signs, definitions,
  event coverage, and source vintages are harmonized.
- No raw shocks, outcomes, Bitcoin monetary-use shares, or empirical findings
  are added by this software change. Synthetic tests verify code behaviour
  only.
