# Sovereign Monetary Architecture (SMA)

A reproducible Python research framework for studying sovereign monetary systems, monetary-policy transmission, monetary autonomy, domestic monetary substitution, and the constraints created by international monetary institutions.

The repository began as the **Bitcoin–Sovereign Monetary Policy Model (BSMPM)**. Its original reduced-form Bitcoin/fiat transmission model remains a foundational component. The research architecture has since expanded to include country-panel econometrics, monetary-authority-aware inference, multi-frequency policy-shock data, source and provenance auditing, Special Drawing Rights (SDR) exposure and sterilisation-cost measures, integrated transmission estimation, identification diagnostics, reproducible data assembly, a researcher-defined autonomy index, and a structural-dynamics scaffold.

**Current implementation: v0.11.0.** The codebase contains analytical and empirical building blocks; it is not yet a calibrated or estimated general-equilibrium model of the international monetary system.

## Research scope

The current architecture covers:

- **Domestic monetary substitution:** reduced-form monetary transmission under fiat/Bitcoin monetary-use shares.
- **Nonlinear adoption dynamics:** alternative transmission functions, critical adoption thresholds, and logistic fixed-point equations with network effects.
- **Sovereign monetary-policy transmission:** country-period panel validation and fixed-effects estimation of heterogeneous policy-shock responses.
- **Monetary institutions:** explicit distinction between country markets and the monetary authorities responsible for policy shocks.
- **Multi-frequency data:** event-level policy shocks aggregated to monthly or quarterly authority-level series, then aligned to country panels.
- **International monetary constraints:** SDR allocations and holdings, foreign-exchange reserves, GDP, exchange-rate deviation measures, and sterilisation-cost proxies.
- **Data governance:** source registries, country-frame audits, missingness summaries, and SHA-256 provenance manifests.\n- **Integrated transmission:** joint policy-shock, Bitcoin monetary-use, and SDR-exposure interaction design.\n- **Identification diagnostics:** within-authority shock variation, cluster counts, and complete-case support.\n- **Reproducible data assembly:** local CSV ingestion, source metadata, file hashes, and validated country-period joins.\n- **Monetary autonomy:** transparent, weighted composite with explicit component directions.\n- **Structural dynamics:** explicit state-transition and quadratic scenario-loss scaffold.

The framework is designed to support the empirical investigation of a central question:

> Under what institutional and external-balance conditions does domestic monetary substitution alter a sovereign monetary authority's effective capacity to transmit policy?

Bitcoin monetary adoption and SDR exposure are distinct constructs. Their interaction is a research question, not an established empirical result.

## Architecture and implementation status

| Component | Module / location | Status |
|---|---|---|
| Reduced-form monetary transmission and adoption dynamics | `src/bsmpm/model.py` | Implemented analytical building blocks |
| Country-period panel validation and fixed-effects estimator | `src/bsmpm/empirical.py` | Implemented baseline estimator |
| CSV ingestion, source registry, and provenance manifests | `src/bsmpm/data_io.py` | Implemented |
| Country roster and source-audit validation | `src/bsmpm/source_audit.py` | Implemented |
| Event-shock aggregation and authority alignment | `src/bsmpm/frequency.py` | Implemented |
| SDR exposure and sterilisation-cost measures | `src/bsmpm/sdr.py` | Implemented |
| Scenario simulation | `src/bsmpm/simulate.py` | Illustrative reduced-form simulation |

The Python package retains the `bsmpm` import namespace for continuity with the original model. The repository's broader name does not imply that every component has already been integrated into one structural model.

## Foundational BSMPM model

The original BSMPM component studies monetary transmission as the fiat/Bitcoin transaction-use share changes. Its reduced-form building blocks include:

- A linear weighted-average transmission coefficient, `K(s) = (1-s)κ_F + sκ_B`.
- An alternative nonlinear transmission parameterisation.
- Critical adoption-threshold calculations.
- A logistic adoption fixed point, `s = Λ(z + ζs)`, allowing multiple equilibria for suitable parameter values.
- Reduced-form seigniorage sensitivity and Bitcoin-sector liquidity-shortfall measures.
- Illustrative adoption-welfare trade-offs and scenario simulation.

Here, `s` denotes a **monetary-use or transaction share**, not Bitcoin's share of household wealth. The linear coefficient is a reduced-form representation; it does not establish that every Bitcoin transaction is insulated from domestic interest rates. The nonlinear form is an alternative specification and must be restricted to economically meaningful parameter values. Multiple fixed points are parameter-dependent: strong feedback alone does not guarantee three roots for every intercept.

These quantities are analytical or illustrative reduced forms. They are not, without further derivation and calibration, accounting identities or measured welfare effects. See [docs/MODEL.md](docs/MODEL.md).

## Country-panel econometrics

The baseline estimator in `bsmpm.empirical` estimates a country-period specification with country and time fixed effects:

```text
outcome ~ policy_shock
        + adoption_share
        + policy_shock × adoption_share
        + controls
        + country FE
        + time FE
```

The interaction coefficient describes how the conditional outcome response associated with a policy shock varies with the measured adoption share, conditional on the included controls and fixed effects.

The estimator supports a configurable clustering variable. Country clustering is the default; where several country markets share one monetary-policy authority, the authority identifier can be used instead. The source-audited frame contains 29 country markets and 20 monetary authorities; ten euro-area markets share the ECB shock series. These are not 29 independent policy-shock authorities.

The estimator is a transparent baseline, not an identification strategy by itself. Causal interpretation requires a defensible shock design and attention to reverse causality, time-varying confounding, measurement error, serial and cross-sectional dependence, and the number of independent clusters. The current authority-clustered implementation uses a one-way clustered sandwich estimator with a finite-sample correction and normal-reference inference; it is not a wild-cluster bootstrap or a two-way clustered estimator. See [docs/EMPIRICAL.md](docs/EMPIRICAL.md) and [docs/PR5_AUTHORITY_MULTIFREQUENCY.md](docs/PR5_AUTHORITY_MULTIFREQUENCY.md).

## Data architecture and measurement discipline

The repository provides validation contracts, templates, source metadata, and provenance tooling. It does **not** bundle a fabricated country-level empirical dataset.

- `bsmpm.data_io` validates country-period data and source-registry metadata, summarizes missing numeric observations, and can create JSON provenance manifests containing SHA-256 file hashes.
- `bsmpm.source_audit` checks the country roster and empirical source catalogue.
- `bsmpm.frequency` aggregates event-level shocks by monetary authority, shock-series identifier, and target period. It retains event counts and does not treat a period with no event as a zero-valued shock by default.
- The frequency workflow keeps event, daily-market, and lower-frequency macroeconomic observations distinct. It does not mechanically interpolate macroeconomic data to daily frequency.

Bitcoin exchange turnover, search interest, broad cryptocurrency indices, and general crypto surveys are not interchangeable with Bitcoin monetary-use shares. They must be labelled according to what they actually measure. Source URLs recorded in the catalogue are metadata; their presence does not mean that data have been fetched, independently authenticated, or cleared for redistribution. See [docs/DATA_INGESTION.md](docs/DATA_INGESTION.md), [docs/PR4_SOURCE_AUDIT.md](docs/PR4_SOURCE_AUDIT.md), and [data/README.md](data/README.md).

## SDR exposure module

The `bsmpm.sdr` module validates country-period SDR and macro-financial inputs and constructs explicitly defined measures, including:

- SDR cumulative allocations relative to GDP.
- SDR holdings relative to foreign-exchange reserves.
- A descriptive difference between SDR holdings and cumulative allocations.
- An SDR-consistent exchange-rate deviation, where the required benchmark and actual exchange-rate inputs are supplied using the same quotation convention.
- An annualised, reduced-form sterilisation-cost proxy, where the required allocation and interest-rate inputs are available.

The holdings-minus-allocations comparison is **not** a complete IMF net-position accounting measure. The exchange-rate deviation requires a documented benchmark; the module does not invent one. The sterilisation-cost measure is a proxy whose interpretation depends on the supplied allocation basis, currency conversion, rates, and period convention. These measures do not, by themselves, establish that SDR arrangements prevent an optimal monetary policy or identify a causal welfare loss.

The repository includes an empty SDR schema template, not observed SDR data. See [docs/PR6_SDR_EXPOSURE.md](docs/PR6_SDR_EXPOSURE.md).

## Integrated transmission, identification, and data pipeline

The `bsmpm.integrated` module composes the policy-shock × Bitcoin-use
interaction with SDR exposure, shock × SDR exposure, and the three-way
shock × Bitcoin-use × SDR-exposure interaction. It defaults to clustering by
monetary-policy authority. This is a conditional-association specification;
causal interpretation still requires an identified shock and defensible
assumptions. See [docs/PR8_INTEGRATED_TRANSMISSION.md](docs/PR8_INTEGRATED_TRANSMISSION.md).

The `bsmpm.identification` module reports pre-estimation design diagnostics:
authority and country counts, within- and between-authority shock dispersion,
authorities with within-authority variation, and within-country Bitcoin-use
variation. These diagnostics do not prove exogeneity, instrument validity, or
parallel trends. See [docs/PR9_IDENTIFICATION.md](docs/PR9_IDENTIFICATION.md).

The `bsmpm.data_pipeline` module loads locally acquired CSV files with
researcher-supplied source metadata and SHA-256 hashes, validates unique
country-period keys, and joins sources without interpolation or imputation.
It does not scrape or download data and does not establish source authenticity
or licensing. See [docs/PR10_DATA_PIPELINE.md](docs/PR10_DATA_PIPELINE.md).

## Sovereign monetary autonomy index

The `bsmpm.autonomy` module constructs a weighted 0–1 index from components
already normalized to [0,1]. Component weights must sum to one, polarity must
be explicit, and missing components are not silently imputed or reweighted.
Bitcoin monetary-use share has no default normative direction and can only be
included with an explicit researcher choice. The composite is a researcher-
defined measure, not an objective sovereignty ranking. See
[docs/PR11_MONETARY_AUTONOMY.md](docs/PR11_MONETARY_AUTONOMY.md).

## Structural-dynamics scaffold

The `bsmpm.structural` module defines a state vector containing inflation,
output, and exchange-rate gaps, Bitcoin monetary-use share, and SDR exposure.
It provides a one-period scenario transition and quadratic scenario loss with
explicit parameters. This is not a solved, estimated, or calibrated
general-equilibrium model; the default parameters are illustrative. See
[docs/PR12_STRUCTURAL_SCAFFOLD.md](docs/PR12_STRUCTURAL_SCAFFOLD.md).

## Requirements and installation

- Python 3.10 or later.
- NumPy and pandas.
- Matplotlib is optional for simulation plots.

Install the package and development dependencies:

```bash
python -m pip install -e ".[dev]"
```

## Quick start

Run the test suite:

```bash
python -m unittest discover -s tests -v
```

Run the illustrative scenario simulation:

```bash
python -m bsmpm.simulate --output outputs
```

## Repository layout

- `src/bsmpm/model.py` — reduced-form analytical model.
- `src/bsmpm/empirical.py` — panel validation and fixed-effects estimator.
- `src/bsmpm/data_io.py` — data ingestion, source registry, and provenance manifests.
- `src/bsmpm/source_audit.py` — country-frame and source-catalogue validation.
- `src/bsmpm/frequency.py` — event-shock aggregation and monetary-authority alignment.
- `src/bsmpm/sdr.py` — SDR exposure validation and derived measures.\n- `src/bsmpm/integrated.py` — integrated monetary-policy transmission specification.\n- `src/bsmpm/identification.py` — pre-estimation identification diagnostics.\n- `src/bsmpm/data_pipeline.py` — documented local data ingestion and assembly.\n- `src/bsmpm/autonomy.py` — weighted monetary-autonomy index.\n- `src/bsmpm/structural.py` — structural-dynamics scenario scaffold.
- `src/bsmpm/simulate.py` — illustrative scenario runner.
- `data/` — documented data contracts and empty templates.
- `tests/` — deterministic unit tests, including synthetic test data.
- `docs/MODEL.md` — foundational BSMPM equations and assumptions.
- `docs/EMPIRICAL.md` — estimator, data contract, and identification limitations.
- `docs/DATA_INGESTION.md` — ingestion and provenance workflow.
- `docs/PR4_SOURCE_AUDIT.md` — country frame, source catalogue, and measurement audit.
- `docs/PR5_AUTHORITY_MULTIFREQUENCY.md` — authority-aware inference and frequency architecture.
- `docs/PR6_SDR_EXPOSURE.md` — SDR data contract, measures, and limitations.\n- `docs/PR8_INTEGRATED_TRANSMISSION.md` — integrated transmission design.\n- `docs/PR9_IDENTIFICATION.md` — identification and design diagnostics.\n- `docs/PR10_DATA_PIPELINE.md` — reproducible empirical data pipeline.\n- `docs/PR11_MONETARY_AUTONOMY.md` — autonomy-index methodology.\n- `docs/PR12_STRUCTURAL_SCAFFOLD.md` — structural-dynamics assumptions.
- `.github/workflows/tests.yml` — continuous integration across Python 3.10–3.12.

## Research roadmap

1. Acquire the source-identified event-level policy shocks and outcome data, and verify access, licensing, and redistribution conditions.
2. Build defensible country-period measures that distinguish Bitcoin ownership, payment and transaction use, settlement use, and contract denomination.
3. Document SDR allocations, holdings, reserve positions, exchange-rate benchmarks, and sterilisation inputs with consistent accounting and currency conventions.
4. Validate shock construction and develop identification strategies appropriate to the monetary-authority structure.
5. Extend inference and robustness analysis for few clusters, serial dependence, cross-sectional dependence, heterogeneous effects, and missing data.
6. Investigate the interaction between domestic monetary substitution, SDR exposure, reserve constraints, and sovereign monetary-policy autonomy.
7. Develop and test a coherent structural or equilibrium framework only after the measurement and identification foundations are established.
8. Publish reproducible data provenance, estimation code, calibration inputs, and reporting metadata.

## Interpretation and reproducibility

Passing unit tests establishes that specified software behaviours work on the tested inputs. It does not validate economic assumptions, data quality, measurement validity, calibration, causal identification, or the truth of a monetary-policy hypothesis. Empirical conclusions require documented observations, defensible constructs, identified variation, robustness analysis, and transparent reporting.

The project therefore treats the distinction between **implemented software**, **measured empirical quantities**, **estimated relationships**, and **theoretical propositions** as a core research-design principle.
