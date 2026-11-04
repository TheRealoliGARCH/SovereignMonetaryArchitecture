# SMA model specification (v0.1)

## 1. Economic meaning of adoption

The core state variable (s\in[0,1]) is the share of relevant domestic activity conducted or contractually denominated in Bitcoin. It is not a proxy for the share of financial wealth held in Bitcoin. Asset ownership, transaction use and contract denomination should be measured separately in empirical work.

## 2. Monetary transmission

The linear reduced form is

[
K(s)=(1-s)\kappa_F+s\kappa_B,
quad \kappa_F\geq\kappa_B\geq0.
]

Its derivative is (K'(s)=\kappa_B-\kappa_F\leq0). Strict attenuation requires (\kappa_F>\kappa_B). The interpretation assumes that the two sector coefficients are comparable weighted transmission sensitivities. It does not imply Bitcoin activity is wholly isolated from domestic rates.

The alternative nonlinear specification is (K(s)=\kappa_F-\alpha s-\beta s^2), with nonnegative parameters. Parameter values must ensure (K(s)\geq0) on the domain used.

## 3. Critical adoption threshold

Given a required minimum (K_{\min}), the linear threshold is

[
s_{crit}=\frac{\kappa_F-K_{\min}}{\kappa_F-\kappa_B},
]

when (\kappa_F>\kappa_B) and (\kappa_B<K_{\min}\leq\kappa_F). If even (s=0) fails the requirement, the requirement is infeasible; if (s=1) still meets it, the threshold is one.

For the quadratic specification, solve (\kappa_F-\alpha s-\beta s^2=K_{\min}) and retain the economically admissible root in [0,1].

The threshold is a model-defined performance boundary, not a universal regulatory or policy threshold.

## 4. Endogenous adoption

The illustrative fixed-point equation is

[
s=\Lambda(z+\zeta s),\qquad
\Lambda(x)=\frac{1}{1+e^{-x}}.
]

Here (z) is an intercept gathering exogenous determinants and (\zeta) is network feedback. Since the maximum logistic derivative is (1/4), (\zeta>4) permits the mapping's slope to exceed one. Multiple intersections require an appropriate intercept; this condition alone does not guarantee three fixed points. Stability reported by the code is local stability under naive fixed-point iteration, not dynamic stability of a full macroeconomic model.

The implemented root search uses a grid scan and bisection. It is a numerical exploration tool, not a formal root-counting certificate.

## 5. Seigniorage

The code includes the illustrative sensitivity expression

[
S(s)=S_0(1-\eta s),\quad 0\leq\eta\leq1.
]

This is a reduced-form proxy. A structural seigniorage equation must derive real money demand and issuance from the household problem and government budget constraint. Bitcoin adoption does not mechanically lower fiat seigniorage one-for-one.

## 6. Liquidity shortfall

The implemented Bitcoin liquidity shortfall is

[
G^{BTC}=\max\{0,L^{BTC}-C^{BTC}-F^{BTC}\}.
]

All amounts are measured in BTC units. Fiat liquidity facilities may still support eligible intermediaries; the expression only measures the uncovered Bitcoin-native liquidity requirement under the stated definitions.

## 7. Welfare

The illustrative welfare function is

[
W(s)=(b_1-c_1)s-\frac12(b_2+c_2)s^2.
]

The unconstrained interior optimum is ((b_1-c_1)/(b_2+c_2)), clipped to [0,1]. This is not a calibrated social-welfare function. Benefits, costs, distributional weights, externalities and first-best benchmark must be specified for policy conclusions.

## 8. What v0.1 does not implement

The package does not yet solve the full household/firm/bank/central-bank general equilibrium. It does not estimate parameters, identify causal monetary shocks, download country data, estimate local projections, or quantify empirically observed adoption thresholds. Those are later research modules.

## 9. Validation principles

- Parameter and domain checks are explicit.
- Numerical outputs are deterministic for fixed inputs.
- Scenario parameters are labelled illustrative.
- Tests validate calculations, not the economic truth of assumptions.
- Empirical datasets require documented definitions, provenance, revisions and missing-data treatment.
