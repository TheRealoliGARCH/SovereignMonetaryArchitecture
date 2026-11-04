import unittest

import numpy as np
import pandas as pd

from bsmpm.integrated import (
    estimate_integrated_transmission,
    prepare_integrated_panel,
)


class IntegratedTransmissionTests(unittest.TestCase):
    def setUp(self):
        rows = []
        for c in range(8):
            for t in range(6):
                shock = float((c + 2 * t) % 5) / 10
                btc = 0.05 + 0.02 * c + 0.01 * t
                sdr = 0.1 + 0.03 * c
                y = 1.2 * shock + 0.4 * btc - 0.2 * sdr + 0.7 * shock * btc * sdr
                rows.append({
                    "country": f"C{c}", "period": f"P{t}",
                    "monetary_policy_authority": f"A{c // 2}",
                    "policy_shock": shock, "btc_use_share": btc,
                    "sdr_exposure": sdr, "outcome": y,
                })
        self.data = pd.DataFrame(rows)

    def test_interactions_are_constructed(self):
        frame = prepare_integrated_panel(self.data)
        self.assertIn("shock_x_sdr", frame)
        self.assertIn("shock_x_btc_x_sdr", frame)
        self.assertAlmostEqual(
            frame.loc[0, "shock_x_btc_x_sdr"],
            frame.loc[0, "policy_shock"] * frame.loc[0, "btc_use_share"] * frame.loc[0, "sdr_exposure"],
        )

    def test_integrated_estimator_uses_authority_clusters(self):
        result = estimate_integrated_transmission(self.data, outcome="outcome")
        self.assertEqual(result.cluster_variable, "monetary_policy_authority")
        self.assertEqual(result.estimate.clusters, 4)
        self.assertIn("shock×btc_use_share×sdr_exposure", result.specification)
        terms = set(result.estimate.coefficients["term"])
        self.assertTrue({"shock_x_adoption", "shock_x_sdr", "shock_x_btc_x_sdr"}.issubset(terms))

    def test_invalid_bitcoin_share_rejected(self):
        bad = self.data.copy()
        bad.loc[0, "btc_use_share"] = 1.2
        with self.assertRaises(ValueError):
            prepare_integrated_panel(bad)


if __name__ == "__main__":
    unittest.main()
