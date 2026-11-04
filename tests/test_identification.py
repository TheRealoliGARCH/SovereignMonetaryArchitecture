import unittest
import pandas as pd

from sma.identification import diagnose_identification


class IdentificationDiagnosticsTests(unittest.TestCase):
    def setUp(self):
        rows = []
        for c in range(6):
            for t in range(4):
                rows.append({
                    "country": f"C{c}", "period": t,
                    "monetary_policy_authority": f"A{c // 2}",
                    "policy_shock": float((c // 2) + t % 2),
                    "btc_use_share": 0.1 + c * 0.02 + t * 0.01,
                })
        self.data = pd.DataFrame(rows)

    def test_reports_authority_structure_and_variation(self):
        result = diagnose_identification(self.data, few_cluster_threshold=10)
        self.assertEqual(result.countries, 6)
        self.assertEqual(result.authorities, 3)
        self.assertGreater(result.authorities_with_within_variation, 0)
        self.assertTrue(any("clusters" in warning for warning in result.warnings))

    def test_rejects_duplicate_country_period(self):
        bad = pd.concat([self.data, self.data.iloc[[0]]], ignore_index=True)
        with self.assertRaises(ValueError):
            diagnose_identification(bad)

    def test_rejects_missing_required_columns(self):
        with self.assertRaises(ValueError):
            diagnose_identification(self.data.drop(columns=["policy_shock"]))


if __name__ == "__main__":
    unittest.main()
