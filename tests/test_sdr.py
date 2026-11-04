import unittest

import numpy as np
import pandas as pd

from sma.sdr import construct_sdr_exposure_metrics, validate_sdr_panel


def sample_sdr_panel():
    return pd.DataFrame({
        "iso3": ["IND", "CHE"],
        "period": ["2024", "2024"],
        "sdr_cumulative_allocations_usd": [10.0, 20.0],
        "sdr_holdings_usd": [8.0, 25.0],
        "fx_reserves_usd": [100.0, 200.0],
        "gdp_usd": [500.0, 1000.0],
        "exchange_rate_lcu_per_usd": [83.0, 0.9],
        "sdr_consistent_exchange_rate_lcu_per_usd": [82.0, 0.92],
        "sdr_allocation_lcu": [830.0, 18.0],
        "policy_rate_pct": [6.5, 1.0],
        "reserve_remuneration_rate_pct": [3.5, 0.5],
    })


class SDRExposureTests(unittest.TestCase):
    def test_validates_country_period_sdr_panel(self):
        summary = validate_sdr_panel(sample_sdr_panel())
        self.assertEqual(summary["rows"], 2)
        self.assertEqual(summary["countries"], 2)
        self.assertEqual(summary["periods"], 1)

    def test_constructs_exposure_ratios_and_stock_comparison(self):
        result = construct_sdr_exposure_metrics(sample_sdr_panel())
        india = result.loc[result["iso3"].eq("IND")].iloc[0]
        self.assertAlmostEqual(india["sdr_allocation_to_gdp"], 0.02)
        self.assertAlmostEqual(india["sdr_holdings_to_fx_reserves"], 0.08)
        self.assertAlmostEqual(
            india["sdr_holdings_minus_cumulative_allocations_usd"], -2.0
        )

    def test_constructs_fx_deviation_and_sterilization_cost(self):
        result = construct_sdr_exposure_metrics(sample_sdr_panel())
        india = result.loc[result["iso3"].eq("IND")].iloc[0]
        self.assertAlmostEqual(
            india["sdr_fx_deviation_log"], np.log(83.0 / 82.0)
        )
        self.assertAlmostEqual(india["sdr_sterilization_cost_lcu"], 24.9)

    def test_rejects_duplicate_country_period(self):
        frame = sample_sdr_panel()
        frame.loc[1, "iso3"] = "IND"
        with self.assertRaisesRegex(ValueError, "unique"):
            validate_sdr_panel(frame)

    def test_rejects_zero_denominator(self):
        frame = sample_sdr_panel()
        frame.loc[0, "gdp_usd"] = 0.0
        with self.assertRaisesRegex(ValueError, "strictly positive"):
            validate_sdr_panel(frame)

    def test_rejects_negative_stock(self):
        frame = sample_sdr_panel()
        frame.loc[0, "sdr_holdings_usd"] = -1.0
        with self.assertRaisesRegex(ValueError, "nonnegative"):
            validate_sdr_panel(frame)

    def test_rejects_nonnumeric_required_stock(self):
        frame = sample_sdr_panel()
        frame["sdr_holdings_usd"] = frame["sdr_holdings_usd"].astype(object)
        frame.loc[0, "sdr_holdings_usd"] = "unknown"
        with self.assertRaisesRegex(ValueError, "nonnumeric"):
            validate_sdr_panel(frame)

    def test_optional_metrics_are_not_invented_when_fields_absent(self):
        frame = sample_sdr_panel().drop(columns=[
            "exchange_rate_lcu_per_usd",
            "sdr_consistent_exchange_rate_lcu_per_usd",
            "sdr_allocation_lcu",
            "policy_rate_pct",
            "reserve_remuneration_rate_pct",
        ])
        result = construct_sdr_exposure_metrics(frame)
        self.assertNotIn("sdr_fx_deviation_log", result.columns)
        self.assertNotIn("sdr_sterilization_cost_lcu", result.columns)


if __name__ == "__main__":
    unittest.main()
