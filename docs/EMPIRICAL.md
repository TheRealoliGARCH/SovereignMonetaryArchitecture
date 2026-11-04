# Empirical panel module (v0.2)

## Research question

Does the response of a monetary outcome to a conventional monetary-policy shock vary with the domestic share of economic activity conducted or contractually denominated in Bitcoin?

The module estimates the reduced-form interaction specification

\[
y_{it}=\beta_0 u_{it}+\beta_1 s_{it}
+\beta_2(u_{it}s_{it})+\gamma'X_{it}
+\mu_i+\tau_t+\varepsilon_{it},
\]

where \(u_{it}\) is a policy-shock measure, \(s_{it}\in[0,1]\) is Bitcoin monetary use, \(X_{it}\) is a vector of controls, and \(\mu_i\), \(\tau_t\) are country and time fixed effects.

The marginal response to the shock is

\[
\frac{\partial E[y_{it}\mid\cdot]}{\partial u_{it}}
=\beta_0+\beta_2s_{it}.
\]

Thus \(\beta_2<0\) is consistent with attenuation as measured Bitcoin monetary use rises, conditional on the specification. It is not by itself a causal finding.

## Implementation

`sma.empirical.validate_panel` checks required columns, unique country-period keys, finite numeric variables, and the [0,1] adoption-share domain. Rows missing any model variable are dropped and counted.

`sma.empirical.estimate_transmission_panel` estimates the model by least squares with explicit country and period indicator variables. It reports coefficients, country-clustered sandwich standard errors with a conventional finite-sample correction, normal-reference p-value approximations, normal-reference 95% intervals, sample size, cluster count, R-squared, and residual degrees of freedom.

The estimator rejects rank-deficient designs and insufficient residual degrees of freedom rather than silently returning unstable estimates.

## Data contract

One row per country-period. Required default columns:

- `country`: stable country identifier.
- `period`: common time-period identifier.
- `outcome`: defined monetary-transmission outcome.
- `policy_shock`: identified or otherwise documented monetary-policy shock.
- `btc_use_share`: Bitcoin monetary-use share, not Bitcoin asset ownership.

Optional controls can be passed by column name. Define outcome units, shock sign convention, frequency, sample coverage, and all transformations before estimation. Missingness is handled by complete-case deletion in this first version; this is transparent but may induce selection bias.

## Source-frame implications (v0.4)

The IMF WP/24/224 sample has 29 country-market observations but 20 monetary
authorities. Ten euro-area country markets share the ECB shock series. The
current country-clustered covariance estimator does not explicitly account
for this common-authority shock structure; estimates using that sample require
an authority-aware inference design before being treated as final.

The source audit also finds no verified globally comparable Bitcoin monetary-
use share. Exchange turnover, search interest, all-crypto composite indices,
and general cryptocurrency surveys are not interchangeable with
`btc_use_share`. Any proxy analysis must use a separate variable name and
be reported as a different estimand. See `docs/PR4_SOURCE_AUDIT.md`.

## Identification and inference limitations

- Country and time fixed effects control for additive, time-invariant country heterogeneity and common period effects; they do not remove time-varying confounding.
- The policy-shock series must be plausibly exogenous for a causal interpretation. Anticipation, endogenous policy responses, measurement error, and omitted time-varying factors remain concerns.
- Bitcoin monetary use may itself respond to monetary conditions. Reverse causality and simultaneity are not solved by this estimator.
- Clustered inference relies on a sufficiently large number of independent country clusters. The reported p-values and intervals use a standard-normal approximation; they are not small-sample t-inference.
- The interaction coefficient is a conditional association unless a defensible identification strategy is supplied.
- The estimator is a reduced-form panel tool, not a DSGE solution and not a calibrated structural model.

## Next empirical requirements

1. Build a country-period dataset with source URLs, retrieval dates, units, revisions, and transformation logs.
2. Separate Bitcoin ownership, payment/transaction use, settlement use, and contract denomination; do not treat them as interchangeable.
3. Document policy-shock construction and test alternative shock series.
4. Pre-register outcome definitions, controls, lags, sample selection, and robustness checks.
5. Investigate IV/local-projection/event-study strategies only where instruments or shock designs are defensible.
6. Assess cross-sectional dependence, serial correlation, heterogeneous treatment effects, and sensitivity to country-cluster counts.
7. Keep synthetic tests separate from empirical findings.

## Reproducibility

The test suite uses a deterministic synthetic panel to check validation, fixed-effects estimation, and the expected direction of a simulated interaction. Synthetic tests validate software behaviour only. They are not empirical evidence about Bitcoin or monetary policy.
