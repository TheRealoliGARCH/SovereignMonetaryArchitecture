import unittest
import pandas as pd

from sma.autonomy import construct_monetary_autonomy_index


class MonetaryAutonomyIndexTests(unittest.TestCase):
    def setUp(self):
        self.data = pd.DataFrame({
            "iso3": ["AAA", "BBB"], "period": ["2025Q1", "2025Q1"],
            "domestic_monetary_control": [0.8, 0.5],
            "exchange_rate_flexibility": [0.6, 0.4],
            "reserve_adequacy": [0.7, 0.8],
            "sdr_exposure": [0.2, 0.6],
        })

    def test_constructs_weighted_index_with_sdr_inverse_polarity(self):
        weights = {
            "domestic_monetary_control": 0.25,
            "exchange_rate_flexibility": 0.25,
            "reserve_adequacy": 0.25,
            "sdr_exposure": 0.25,
        }
        result = construct_monetary_autonomy_index(self.data, weights=weights)
        self.assertAlmostEqual(result.loc[0, "monetary_autonomy_index"], 0.725)
        self.assertAlmostEqual(result.loc[1, "monetary_autonomy_index"], 0.525)

    def test_requires_weights_to_sum_to_one(self):
        with self.assertRaises(ValueError):
            construct_monetary_autonomy_index(
                self.data, weights={"domestic_monetary_control": 0.5}
            )

    def test_requires_explicit_bitcoin_use_polarity(self):
        data = self.data.assign(btc_use_share=[0.2, 0.4])
        weights = {"domestic_monetary_control": 0.5, "btc_use_share": 0.5}
        with self.assertRaises(ValueError):
            construct_monetary_autonomy_index(data, weights=weights)
        result = construct_monetary_autonomy_index(
            data, weights=weights,
            directions={"btc_use_share": 1},
        )
        self.assertIn("monetary_autonomy_index", result)

    def test_rejects_missing_component_values(self):
        data = self.data.copy()
        data.loc[0, "reserve_adequacy"] = None
        weights = {k: 0.25 for k in [
            "domestic_monetary_control", "exchange_rate_flexibility",
            "reserve_adequacy", "sdr_exposure",
        ]}
        with self.assertRaises(ValueError):
            construct_monetary_autonomy_index(data, weights=weights)


if __name__ == "__main__":
    unittest.main()
