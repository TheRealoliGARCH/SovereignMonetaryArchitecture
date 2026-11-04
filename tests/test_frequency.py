import unittest

import pandas as pd

from bsmpm.frequency import aggregate_event_shocks, attach_authority_shocks


class TestFrequencyArchitecture(unittest.TestCase):
    def test_monthly_event_shocks_sum_by_authority_and_series(self):
        events = pd.DataFrame({
            "announcement_datetime_utc": [
                "2024-01-03T10:00:00Z", "2024-01-20T12:00:00Z",
                "2024-02-02T09:00:00Z",
            ],
            "monetary_policy_authority": ["ECB", "ECB", "RBI"],
            "shock_series_id": ["ECB_OIS", "ECB_OIS", "RBI_OIS"],
            "epsilon_mp_bp": [2.0, -0.5, 1.25],
            "epsilon_cbi_bp": [0.2, 0.1, -0.1],
        })
        result = aggregate_event_shocks(events)
        jan = result.loc[result["period"].eq("2024-01")].iloc[0]
        self.assertEqual(jan["monetary_policy_authority"], "ECB")
        self.assertAlmostEqual(jan["epsilon_mp_bp"], 1.5)
        self.assertEqual(jan["event_count"], 2)

    def test_rejects_unsupported_frequency(self):
        with self.assertRaisesRegex(ValueError, "frequency"):
            aggregate_event_shocks(pd.DataFrame(), frequency="D")

    def test_maps_shared_authority_shock_to_multiple_markets(self):
        panel = pd.DataFrame({
            "country": ["DEU", "FRA"], "period": ["2024-01", "2024-01"],
            "outcome": [1.0, 2.0],
        })
        roster = pd.DataFrame({
            "country": ["DEU", "FRA"],
            "monetary_policy_authority": ["ECB", "ECB"],
            "shock_series_id": ["ECB_OIS", "ECB_OIS"],
        })
        shocks = pd.DataFrame({
            "monetary_policy_authority": ["ECB"], "shock_series_id": ["ECB_OIS"],
            "period": ["2024-01"], "epsilon_mp_bp": [1.5], "event_count": [2],
        })
        result = attach_authority_shocks(panel, roster, shocks)
        self.assertEqual(len(result), 2)
        self.assertEqual(result["epsilon_mp_bp"].tolist(), [1.5, 1.5])

    def test_rejects_missing_authority_period_shock(self):
        panel = pd.DataFrame({"country": ["DEU"], "period": ["2024-02"]})
        roster = pd.DataFrame({
            "country": ["DEU"], "monetary_policy_authority": ["ECB"],
            "shock_series_id": ["ECB_OIS"],
        })
        shocks = pd.DataFrame({
            "monetary_policy_authority": ["ECB"], "shock_series_id": ["ECB_OIS"],
            "period": ["2024-01"], "epsilon_mp_bp": [1.5],
        })
        with self.assertRaisesRegex(ValueError, "lack an authority-period shock"):
            attach_authority_shocks(panel, roster, shocks)


if __name__ == "__main__":
    unittest.main()
