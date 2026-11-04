# Bitcoin–Sovereign Monetary Policy Model (BSMPM)

A reproducible Python implementation of the model architecture developed in the accompanying research discussion. The first release implements transparent reduced-form building blocks; it is **not yet a calibrated or estimated general-equilibrium model**.

## Scope

- Monetary transmission under fiat/Bitcoin transaction shares.
- Nonlinear transmission attenuation and critical adoption thresholds.
- Endogenous Bitcoin-adoption fixed points with logistic network effects.
- Reduced-form seigniorage sensitivity.
- Bitcoin-sector liquidity shortfall.
- Illustrative adoption-welfare trade-offs.
- Scenario simulation and CSV output.
- Unit tests and continuous integration.

## Model conventions

All functions validate domains and document their assumptions. In particular:

1. The adoption share (s) is a *monetary-use/transaction share*, not the Bitcoin share of household wealth.
2. The transmission coefficient (K(s)=(1-s)\kappa_F+s\kappa_B) is a reduced-form weighted average. It does not establish that every Bitcoin transaction is insulated from domestic rates.
3. The nonlinear function (K(s)=\kappa_F-\alpha s-\beta s^2) is an alternative parameterization and must be constrained to economically meaningful values over the domain being studied.
4. The adoption fixed-point equation is (s=\Lambda(z+\zeta s)). Multiple fixed points are possible when feedback is sufficiently strong; (zeta>4) is a sufficient condition for the mapping's slope to exceed one somewhere, not a guarantee of three roots for every intercept.
5. Seigniorage sensitivity and welfare are illustrative reduced forms, not accounting identities or calibrated welfare estimates.
6. No external dataset is bundled. Simulations use explicitly labelled illustrative parameters.

## Requirements

Python 3.10+; NumPy, pandas and Matplotlib for the simulation command. The core library and tests use only the Python standard library.

Install:

```bash
python -m pip install -e ".[dev]"
```

## Quick start

Run tests:

```bash
python -m unittest discover -s tests -v
```

Run the illustrative scenarios:

```bash
python -m bsmpm.simulate --output outputs
```

The command writes scenario results and a parameter-sensitivity table to CSV. Figures are optional and generated only when Matplotlib is installed.

## Repository layout

- `src/bsmpm/model.py`: validated analytical functions.
- `src/bsmpm/simulate.py`: reproducible scenario runner.
- `tests/`: deterministic unit and property-boundary tests.
- `docs/MODEL.md`: equations, assumptions, limitations and extension roadmap.
- `.github/workflows/tests.yml`: CI.

## Research roadmap

1. Replace illustrative parameter values with documented country-level data.
2. Estimate adoption and monetary-transmission equations, addressing reverse causality.
3. Add household and firm optimality conditions and solve a coherent DSGE/general-equilibrium model.
4. Add explicit commercial-bank balance sheets, maturity/currency mismatch and central-bank collateral rules.
5. Conduct welfare analysis against a clearly specified first-best benchmark.
6. Publish calibration files, data provenance, estimation code and reproducibility metadata.

## Interpretation

A successful test suite verifies the software implementation of the stated equations. It does not validate the economic assumptions or establish causal effects. Empirical conclusions require identified shocks, defensible adoption measures, and robustness analysis.
