import unittest

import numpy as np
import pandas as pd

from bsmpm.empirical import estimate_transmission_panel, validate_panel


def sample_panel(seed=17):
    rng = np.random.default_rng(seed)
    rows = []
    countries = [f"C{i}" for i in range(12)]
    periods = list(range(10))
    country_effect = {c: rng.normal() for c in countries}
    time_effect = {t: rng.normal(scale=0.3) for t in periods}
    for i, country in enumerate(countries):
        for period in periods:
            adoption = float(np.clip(
                0.10 + 0.035 * i + 0.012 * period + rng.normal(scale=0.025),
                0.02, 0.90,
            ))
            shock = rng.normal()
            outcome = (
                country_effect[country] + time_effect[period]
                + 0.7 * shock - 0.45 * shock * adoption
                + rng.normal(scale=0.08)
            )
            rows.append({
                "country": country, "period": period, "outcome": outcome,
                "policy_shock": shock, "btc_use_share": adoption,
            })
    return pd.DataFrame(rows)


class TestPanelValidation(unittest.TestCase):
    def test_unique_country_period_required(self):
        frame = sample_panel()
        frame = pd.concat([frame, frame.iloc[[0]]], ignore_index=True)
        with self.assertRaisesRegex(ValueError, "unique"):
            validate_panel(frame, outcome="outcome", shock="policy_shock",
                           adoption="btc_use_share")

    def test_adoption_share_bounds(self):
        frame = sample_panel()
        frame.loc[0, "btc_use_share"] = 1.2
        with self.assertRaisesRegex(ValueError, r"\[0, 1\]"):
            validate_panel(frame, outcome="outcome", shock="policy_shock",
                           adoption="btc_use_share")

    def test_missing_model_rows_are_counted(self):
        frame = sample_panel()
        frame.loc[0, "outcome"] = np.nan
        clean, dropped = validate_panel(
            frame, outcome="outcome", shock="policy_shock", adoption="btc_use_share"
        )
        self.assertEqual(dropped, 1)
        self.assertEqual(len(clean), len(frame) - 1)


class TestPanelEstimator(unittest.TestCase):
    def test_recovers_interaction_direction_with_two_way_fe(self):
        result = estimate_transmission_panel(
            sample_panel(), outcome="outcome", shock="policy_shock",
            adoption="btc_use_share",
        )
        coef = result.coefficients.set_index("term")["coefficient"]
        self.assertGreater(coef["policy_shock"], 0.4)
        self.assertLess(coef["shock_x_adoption"], 0.0)
        self.assertEqual(result.nobs, 120)
        self.assertEqual(result.clusters, 12)
        self.assertGreater(result.residual_degrees_of_freedom, 0)

    def test_authority_cluster_count_is_reported(self):
        frame = sample_panel()
        frame["authority"] = frame["country"].map(
            lambda value: f"A{int(value[1:]) // 2}"
        )
        frame.loc[0, "outcome"] = np.nan
        result = estimate_transmission_panel(
            frame, outcome="outcome", shock="policy_shock",
            adoption="btc_use_share", cluster_by="authority",
        )
        self.assertEqual(result.clusters, 6)
        self.assertEqual(result.dropped_rows, 1)

    def test_missing_columns_fail_clearly(self):
        with self.assertRaisesRegex(ValueError, "missing required"):
            estimate_transmission_panel(
                pd.DataFrame({"country": ["A"], "period": [1]}),
                outcome="outcome", shock="policy_shock", adoption="btc_use_share",
            )


if __name__ == "__main__":
    unittest.main()
