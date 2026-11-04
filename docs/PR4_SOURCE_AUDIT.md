# BSMPM v0.4: country frame and empirical source audit

## Purpose and scope

This release turns the v0.3 empty schema into a source-audited empirical design.
It adds a reproducible 29-country market frame and a catalogue of candidate
series, definitions, units, frequencies, coverage, retrieval dates, reuse
constraints and admissible analytical roles.

**It does not claim to contain a complete observed country-period panel.** The
underlying high-frequency monetary-policy shock data described in the selected
IMF paper are built from Refinitiv/Bloomberg inputs; public access to a
redistributable event-level file has not been verified. No country observations
are fabricated or scraped into the repository.

## Country frame

`data/country_roster.csv` records the 29 country markets listed in Bolhuis,
Das and Yao (IMF WP/24/224): 21 advanced economies and 8 emerging markets,
with daily monetary-policy shock sample coverage reported as 2000-2022.

The country count is not the count of independent monetary-policy authorities.
The paper describes 20 central banks and 29 country markets because ten euro
area country markets share the ECB monetary-policy authority and common
Eurozone shock series. The roster therefore records both
`monetary_policy_authority` and `shock_series_id`. These ten country rows must
not be treated as ten independent policy shocks.

The paper contains a small internal count discrepancy: its abstract and
classification list imply 21 advanced economies plus 8 emerging markets,
whereas one Annex I sentence says 22 advanced economies plus 8 emerging
markets despite also stating 29 total countries. The roster follows the
abstract and the explicit 21-country advanced-economy list, giving 29 in total.
This discrepancy is retained here rather than silently resolved.

## Shock measurement

The preferred treatment is the identified monetary-policy shock component
(`epsilon_MP`) from the IMF WP/24/224 decomposition, not the raw change in
the one-year interest-rate swap (IRS) rate. Preserve distinct columns for:

- raw monetary-policy surprise (`mps`);
- orthogonalized surprise (`mps_orthogonalized`);
- identified monetary-policy shock (`epsilon_mp`);
- central-bank-information shock (`epsilon_cbi`);
- announcement date, local time, announcement type, and source authority.

The paper uses daily changes in one-year IRS rates around policy
announcements, generally with overnight-indexed swaps where available and
shortest-tenor floating indices otherwise. It separately models central-bank
response-to-news and central-bank-information components. Its source inputs
include Refinitiv DataStream swap rates and Bloomberg Economic Calendar
announcement data. A public working paper describes the dataset and method;
the underlying input data may require commercial access and rights clearance.

**Important econometric implication:** the euro-area shock is common across ten
country markets. Country-clustered standard errors alone do not correct
dependence induced by a shared monetary authority. Any estimation using this
sample must account for the authority-level shock structure and the limited
number of independent policy authorities. The current v0.2 estimator is a
baseline and is not yet authority-cluster aware.

## Bitcoin measurement audit

The target construct in the original BSMPM panel is a Bitcoin monetary-use
share, not Bitcoin ownership or portfolio allocation. The source review finds
no verified, globally comparable country-period series of the share of
transactions, payments, settlement, or contracts denominated in Bitcoin.

Available candidates are proxies with different meanings:

1. **IMF Bitcoin exchange-volume proxy (2013-2019):** an IMF Fintech Note
   reports Bitcoin exchange trading volumes for local-currency pairs across
   47 countries and Google search interest across 145 countries. The Note
   explicitly warns that trade direction is unobserved, exchange coverage is
   incomplete, and trading volumes may not closely track adoption. This is a
   market-activity proxy, not a payments share.
2. **Google Trends Bitcoin search interest:** relative attention normalized
   to a 0-100 scale within the selected query/geography/time window. It is
   not a user count or a measure of monetary use.
3. **Chainalysis 2026 Global Crypto Adoption Index:** an all-crypto composite
   based on service flows, domestic P2P, cross-border flows and balances for
   117 countries. Its geography assignment partly uses service web traffic.
   It is not Bitcoin-only and includes asset balances; underlying data and
   methodology are proprietary.
4. **Federal Reserve SHED:** US-only survey data separate investment/holding
   from payment and remittance use, but the question wording includes
   cryptocurrencies such as Bitcoin or Ethereum. It is useful for construct
   validation, not a cross-country Bitcoin-specific panel.
5. **World Bank Global Findex:** comparable financial inclusion and digital
   payment indicators across survey waves; it is not a Bitcoin-use survey.

None of these sources is silently mapped to `btc_use_share`. The source
catalogue records their permissible roles. A future proxy specification should
use a different variable name and be estimated as a separately labelled
proxy model, with sensitivity analysis.

## Source catalogue

`data/source_catalog.csv` contains source metadata using the v0.3 registry
contract. All retrieval dates refer to the audit date shown in the catalogue;
they are not observation-level data retrieval dates. URLs identify the source
documentation or download portal. Status fields explicitly distinguish
published descriptions from downloaded data.

Core source roles:

| Construct | Candidate source | Admissible role |
| --- | --- | --- |
| Identified monetary-policy shock | IMF WP/24/224 | Preferred treatment, subject to obtaining data and reuse clearance |
| Policy-rate stance | BIS CBPOL | Policy control / validation, not an exogenous shock |
| Macro controls | IMF WEO | Annual controls, with series-level coverage and vintage checks |
| Bitcoin market activity | IMF Fintech Note 2022/005 | Proxy only; not monetary-use share |
| Bitcoin search attention | Google Trends | Attention proxy only |
| General digital finance | World Bank Global Findex | Context/control, not BTC use |
| All-crypto activity | Chainalysis 2026 | External robustness proxy only, subject to access rights |
| Transaction-use survey | Federal Reserve SHED | US-only construct validation |

## Frequency and panel architecture

Do not force all sources into a single frequency by mechanical interpolation.
Retain separate linked tables:

- `shock_events`: one row per policy announcement and shock authority;
- `market_outcomes_daily`: country-market daily asset-price outcomes;
- `macro_country_period`: monthly or quarterly country outcomes and controls;
- `bitcoin_measurements`: native-frequency survey or proxy measures with
  construct and source identifiers.

For each derived panel, publish the aggregation rule (e.g. sum of event shocks
within month/quarter), event-to-period mapping, time zone, and treatment of
multiple announcements. Annual crypto proxies cannot be expanded into daily
observations as if they were measured daily.

## Next data acquisition gate

Before estimation, obtain and license-cleared source extracts; record
observation-level retrieval/vintage metadata; map authority-level shocks to
country markets without duplicating independent shock counts; and decide
whether the estimand is about direct Bitcoin monetary use or a clearly labelled
market-activity proxy. If direct use remains unmeasured, the baseline
`btc_use_share` specification remains unestimated rather than filled with an
incompatible proxy.

## References

- Bolhuis, M. A., Das, S., and Yao, B. (2024). *A New Dataset of High-Frequency
  Monetary Policy Shocks*. IMF Working Paper 2024/224.
- He, D., Kokenyne Ivanics, A., Lavayssière, X., Lukonga, I., Schwarz, N.,
  Sugimoto, N., and Verrier, J. (2022). *Capital Flow Management Measures in
  the Digital Age: Challenges of Crypto Assets*. IMF Fintech Note 2022/005.
- Bank for International Settlements. *Central bank policy rates: data
  documentation and sources*.
- World Bank. *Global Findex Database 2025*.
- Board of Governors of the Federal Reserve System. *Report on the Economic
  Well-Being of U.S. Households in 2024*.
